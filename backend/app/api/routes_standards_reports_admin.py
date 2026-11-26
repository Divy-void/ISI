import csv
import io
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_admin
from app.database.session import get_db
from app.models.models import (
    StandardCatalogue,
    SavedStandard,
    Report,
    AnalysisCase,
    AuditEvent,
    User,
)
from app.schemas.schemas import StandardIn

router = APIRouter(prefix="/api", tags=["standards-reports-admin"])


@router.get("/standards")
def list_standards(db: Session = Depends(get_db)):
    return db.query(StandardCatalogue).order_by(StandardCatalogue.catalogue_id.asc()).all()


@router.get("/standards/search")
def search_standards(
    q: Optional[str] = Query(default=""),
    sector: Optional[str] = Query(default=""),
    category: Optional[str] = Query(default=""),
    db: Session = Depends(get_db),
):
    items = db.query(StandardCatalogue).all()
    q_lower = (q or "").strip().lower()
    sec_lower = (sector or "").strip().lower()
    cat_lower = (category or "").strip().lower()

    results = []
    for s in items:
        if sec_lower and sec_lower != "all" and s.sector.lower() != sec_lower:
            continue
        if cat_lower and cat_lower != "all" and cat_lower not in [c.lower() for c in (s.related_requirement_categories or [])]:
            continue
        if q_lower:
            haystack = f"{s.catalogue_id} {s.title} {s.sector} {s.product_category} {s.description} {s.scope} {' '.join(s.technical_keywords or [])}".lower()
            if q_lower not in haystack:
                continue
        results.append(s)
    return results


@router.get("/standards/{standard_id}")
def get_standard(standard_id: int, db: Session = Depends(get_db)):
    s = db.query(StandardCatalogue).filter(StandardCatalogue.id == standard_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Standard not found")
    return s


@router.post("/standards")
def create_standard(
    payload: StandardIn,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(StandardCatalogue).filter(StandardCatalogue.catalogue_id == payload.catalogue_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Catalogue ID already exists.")
    std = StandardCatalogue(**payload.model_dump())
    db.add(std)
    db.add(AuditEvent(
        user_id=admin_user.id,
        username=admin_user.username,
        action="CREATE_STANDARD",
        entity_type="standard",
        entity_id=payload.catalogue_id,
        details=f"Added demo catalogue record {payload.catalogue_id}",
    ))
    db.commit()
    db.refresh(std)
    return std


@router.put("/standards/{standard_id}")
def update_standard(
    standard_id: int,
    payload: StandardIn,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    std = db.query(StandardCatalogue).filter(StandardCatalogue.id == standard_id).first()
    if not std:
        raise HTTPException(status_code=404, detail="Standard not found")
    for k, v in payload.model_dump().items():
        setattr(std, k, v)
    db.add(AuditEvent(
        user_id=admin_user.id,
        username=admin_user.username,
        action="UPDATE_STANDARD",
        entity_type="standard",
        entity_id=std.catalogue_id,
        details=f"Updated demo catalogue record {std.catalogue_id}",
    ))
    db.commit()
    db.refresh(std)
    return std


@router.get("/saved-standards")
def list_saved_standards(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.query(SavedStandard).filter(SavedStandard.user_id == current_user.id).all()
    return [
        {
            "id": s.id,
            "standard_id": s.standard_id,
            "saved_at": s.saved_at.isoformat() if s.saved_at else None,
            "standard": s.standard,
        }
        for s in saved
    ]


@router.post("/saved-standards")
def save_standard(
    standard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(SavedStandard)
        .filter(SavedStandard.user_id == current_user.id, SavedStandard.standard_id == standard_id)
        .first()
    )
    if existing:
        return {"id": existing.id, "message": "Already saved"}
    item = SavedStandard(user_id=current_user.id, standard_id=standard_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "message": "Standard saved"}


@router.delete("/saved-standards/{saved_id}")
def delete_saved_standard(
    saved_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(SavedStandard)
        .filter(SavedStandard.id == saved_id, SavedStandard.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Saved item not found")
    db.delete(item)
    db.commit()
    return {"message": "Removed from saved standards"}


@router.post("/analyses/{analysis_id}/reports")
def generate_report(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    a = db.query(AnalysisCase).filter(AnalysisCase.id == analysis_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Analysis not found")

    doc = a.documents[0] if a.documents else None
    report_code = f"RPT-{uuid.uuid4().hex[:8].upper()}"
    snapshot = {
        "disclaimer": "Demonstration output. Recommendations are decision-support suggestions based on the demonstration catalogue and require verification against authoritative sources.",
        "analysis": {
            "id": a.id,
            "title": a.title,
            "category": a.category,
            "department_name": a.department_name,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        },
        "document": {
            "filename": doc.filename if doc else "N/A",
            "file_type": doc.file_type if doc else "N/A",
            "page_count": doc.page_count if doc else 0,
        },
        "requirements": [
            {
                "req_code": r.req_code,
                "description": r.description,
                "category": r.category,
                "criticality": r.criticality,
                "units_or_conditions": r.units_or_conditions,
                "source_location": r.source_location,
            }
            for r in a.requirements
        ],
        "recommendations": [
            {
                "catalogue_id": rec.standard.catalogue_id,
                "title": rec.standard.title,
                "sector": rec.standard.sector,
                "relevance_score": rec.relevance_score,
                "match_label": rec.match_label,
                "explanation": rec.explanation,
                "addressed_req_codes": rec.addressed_req_codes,
                "unaddressed_req_codes": rec.unaddressed_req_codes,
                "verification_status": rec.standard.verification_status,
                "decision": rec.decision.decision if rec.decision else "pending",
                "comments": rec.decision.comments if rec.decision else "",
            }
            for rec in sorted(a.recommendations, key=lambda x: x.relevance_score, reverse=True)
        ],
    }

    report = Report(
        report_code=report_code,
        analysis_id=a.id,
        generated_by_id=current_user.id,
        summary_snapshot=snapshot,
    )
    db.add(report)
    db.add(AuditEvent(
        user_id=current_user.id,
        username=current_user.username,
        action="GENERATE_REPORT",
        entity_type="report",
        entity_id=report_code,
        details=f"Generated report {report_code} for analysis '{a.title}'",
    ))
    db.commit()
    db.refresh(report)
    return {
        "id": report.id,
        "report_code": report.report_code,
        "analysis_id": report.analysis_id,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "summary_snapshot": report.summary_snapshot,
    }


@router.get("/reports")
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "report_code": r.report_code,
            "analysis_id": r.analysis_id,
            "analysis_title": r.analysis.title if r.analysis else "Unknown",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]


@router.get("/reports/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "id": r.id,
        "report_code": r.report_code,
        "analysis_id": r.analysis_id,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "summary_snapshot": r.summary_snapshot,
    }


@router.get("/reports/{report_id}/csv")
def export_report_csv(report_id: int, db: Session = Depends(get_db)):
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")

    snap = r.summary_snapshot or {}
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["IS-Assist Demonstration Report", r.report_code])
    writer.writerow(["Disclaimer", snap.get("disclaimer", "")])
    writer.writerow([])
    writer.writerow(["Catalogue ID", "Title", "Sector", "Demo Relevance Score", "Match Label", "Reviewer Decision", "Verification Status", "Addressed Requirements"])
    for rec in snap.get("recommendations", []):
        writer.writerow([
            rec.get("catalogue_id"),
            rec.get("title"),
            rec.get("sector"),
            rec.get("relevance_score"),
            rec.get("match_label"),
            rec.get("decision"),
            rec.get("verification_status"),
            "; ".join(rec.get("addressed_req_codes", [])),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={r.report_code}.csv"},
    )


@router.get("/admin/users")
def admin_users(admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "department_name": u.department.name if u.department else "General",
        }
        for u in users
    ]


@router.get("/admin/audit")
def admin_audit(admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    events = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(50).all()
    return [
        {
            "id": e.id,
            "username": e.username,
            "action": e.action,
            "entity_type": e.entity_type,
            "entity_id": e.entity_id,
            "details": e.details,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]


@router.get("/admin/catalogue")
def admin_catalogue(admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(StandardCatalogue).order_by(StandardCatalogue.catalogue_id.asc()).all()

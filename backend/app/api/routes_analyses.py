import os
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.config import settings
from app.database.seed import SAMPLE_TENDER_TEXT
from app.database.session import get_db
from app.document_processing.parser import parse_document
from app.ai.extractor import extract_requirements_from_text
from app.recommendation.engine import compute_recommendation
from app.models.models import (
    AnalysisCase,
    UploadedDocument,
    ExtractedRequirement,
    StandardCatalogue,
    Recommendation,
    RequirementStandardMapping,
    ReviewerDecision,
    AuditEvent,
    User,
)
from app.schemas.schemas import AnalysisCreate, RequirementsBulkUpdate, DecisionIn

router = APIRouter(prefix="/api", tags=["analyses"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/analyses")
def create_analysis(
    payload: AnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = AnalysisCase(
        title=payload.title,
        category=payload.category,
        department_name=payload.department_name,
        context_notes=payload.context_notes or "",
        status="created",
        progress_step=1,
        is_sample=payload.is_sample,
        created_by_id=current_user.id,
    )
    db.add(analysis)
    db.flush()

    text_to_store = SAMPLE_TENDER_TEXT if payload.is_sample else (payload.pasted_text or "").strip()
    if text_to_store:
        doc = UploadedDocument(
            analysis_id=analysis.id,
            filename="sample_municipal_led_street_lighting_tender.txt" if payload.is_sample else "pasted_tender_text.txt",
            file_type="pasted",
            file_size_bytes=len(text_to_store.encode("utf-8")),
            extracted_text=text_to_store,
            page_count=1,
            parse_status="parsed",
            parse_note="Sample tender loaded." if payload.is_sample else "Pasted tender text loaded.",
        )
        db.add(doc)

    db.add(AuditEvent(
        user_id=current_user.id,
        username=current_user.username,
        action="CREATE_ANALYSIS",
        entity_type="analysis",
        entity_id=str(analysis.id),
        details=f"Created analysis '{analysis.title}'",
    ))
    db.commit()
    db.refresh(analysis)
    return {
        "id": analysis.id,
        "title": analysis.title,
        "category": analysis.category,
        "department_name": analysis.department_name,
        "status": analysis.status,
        "is_sample": analysis.is_sample,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
    }


@router.get("/analyses")
def list_analyses(db: Session = Depends(get_db)):
    items = db.query(AnalysisCase).order_by(AnalysisCase.created_at.desc()).all()
    result = []
    for a in items:
        doc = a.documents[0] if a.documents else None
        result.append({
            "id": a.id,
            "title": a.title,
            "category": a.category,
            "department_name": a.department_name,
            "status": a.status,
            "is_sample": a.is_sample,
            "filename": doc.filename if doc else None,
            "requirements_count": len(a.requirements),
            "recommendations_count": len(a.recommendations),
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })
    return result


@router.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    a = db.query(AnalysisCase).filter(AnalysisCase.id == analysis_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Analysis not found")
    doc = a.documents[0] if a.documents else None
    return {
        "id": a.id,
        "title": a.title,
        "category": a.category,
        "department_name": a.department_name,
        "context_notes": a.context_notes,
        "status": a.status,
        "progress_step": a.progress_step,
        "error_message": a.error_message,
        "is_sample": a.is_sample,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "document": {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size_bytes": doc.file_size_bytes,
            "page_count": doc.page_count,
            "parse_status": doc.parse_status,
            "parse_note": doc.parse_note,
        } if doc else None,
    }


@router.post("/analyses/{analysis_id}/upload")
async def upload_document(
    analysis_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    a = db.query(AnalysisCase).filter(AnalysisCase.id == analysis_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Analysis not found")

    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: PDF, DOCX, TXT.")

    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit.")

    safe_name = f"{uuid.uuid4().hex}_{Path(file.filename or 'doc').name}"
    dest_path = os.path.join(settings.STORAGE_DIR, safe_name)
    with open(dest_path, "wb") as f:
        f.write(content)

    file_type = ext.lstrip(".")
    extracted_text, page_count, parse_status, parse_note = parse_document(dest_path, file_type)

    doc = UploadedDocument(
        analysis_id=a.id,
        filename=file.filename or safe_name,
        file_type=file_type,
        file_size_bytes=len(content),
        storage_path=dest_path,
        extracted_text=extracted_text,
        page_count=page_count,
        parse_status=parse_status,
        parse_note=parse_note,
    )
    db.add(doc)
    a.status = "uploading"
    a.progress_step = 2

    db.add(AuditEvent(
        user_id=current_user.id,
        username=current_user.username,
        action="UPLOAD_DOCUMENT",
        entity_type="analysis",
        entity_id=str(a.id),
        details=f"Uploaded '{doc.filename}' ({parse_status})",
    ))
    db.commit()
    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "parse_status": doc.parse_status,
        "parse_note": doc.parse_note,
        "page_count": doc.page_count,
    }


@router.post("/analyses/{analysis_id}/process")
def process_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    a = db.query(AnalysisCase).filter(AnalysisCase.id == analysis_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Analysis not found")

    doc = a.documents[0] if a.documents else None
    if not doc or not doc.extracted_text.strip():
        a.status = "failed"
        a.error_message = doc.parse_note if doc else "No document or tender text available."
        db.commit()
        raise HTTPException(status_code=400, detail=a.error_message)

    # Clear previous requirements if re-processing
    db.query(ExtractedRequirement).filter(ExtractedRequirement.analysis_id == a.id).delete()

    extracted = extract_requirements_from_text(doc.extracted_text, source_document=doc.filename)
    for item in extracted:
        db.add(ExtractedRequirement(analysis_id=a.id, **item))

    a.status = "awaiting_review"
    a.progress_step = 4
    a.error_message = None

    db.add(AuditEvent(
        user_id=current_user.id,
        username=current_user.username,
        action="EXTRACT_REQUIREMENTS",
        entity_type="analysis",
        entity_id=str(a.id),
        details=f"Extracted {len(extracted)} requirements from '{doc.filename}'",
    ))
    db.commit()
    return {"status": a.status, "extracted_count": len(extracted)}


@router.get("/analyses/{analysis_id}/status")
def get_analysis_status(analysis_id: int, db: Session = Depends(get_db)):
    a = db.query(AnalysisCase).filter(AnalysisCase.id == analysis_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "id": a.id,
        "status": a.status,
        "progress_step": a.progress_step,
        "error_message": a.error_message,
    }


@router.get("/analyses/{analysis_id}/requirements")
def get_requirements(analysis_id: int, db: Session = Depends(get_db)):
    reqs = (
        db.query(ExtractedRequirement)
        .filter(ExtractedRequirement.analysis_id == analysis_id)
        .order_by(ExtractedRequirement.id.asc())
        .all()
    )
    return [
        {
            "id": r.id,
            "analysis_id": r.analysis_id,
            "req_code": r.req_code,
            "description": r.description,
            "category": r.category,
            "keywords": r.keywords or [],
            "units_or_conditions": r.units_or_conditions,
            "criticality": r.criticality,
            "source_document": r.source_document,
            "source_location": r.source_location,
            "evidence_text": r.evidence_text,
            "confidence": r.confidence,
            "review_status": r.review_status,
            "is_confirmed": r.is_confirmed,
        }
        for r in reqs
    ]


@router.put("/analyses/{analysis_id}/requirements")
def update_requirements(
    analysis_id: int,
    payload: RequirementsBulkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    a = db.query(AnalysisCase).filter(AnalysisCase.id == analysis_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Analysis not found")

    db.query(ExtractedRequirement).filter(ExtractedRequirement.analysis_id == analysis_id).delete()
    for idx, item in enumerate(payload.requirements, start=1):
        code = item.req_code or f"REQ-{idx:03d}"
        db.add(ExtractedRequirement(
            analysis_id=analysis_id,
            req_code=code,
            description=item.description,
            category=item.category,
            keywords=item.keywords,
            units_or_conditions=item.units_or_conditions,
            criticality=item.criticality,
            source_document=item.source_document,
            source_location=item.source_location,
            evidence_text=item.evidence_text or item.description,
            confidence=item.confidence,
            review_status=item.review_status,
            is_confirmed=item.is_confirmed,
        ))

    db.add(AuditEvent(
        user_id=current_user.id,
        username=current_user.username,
        action="UPDATE_REQUIREMENTS",
        entity_type="analysis",
        entity_id=str(analysis_id),
        details=f"Confirmed/updated {len(payload.requirements)} requirements.",
    ))
    db.commit()
    return {"message": "Requirements updated", "count": len(payload.requirements)}


@router.post("/analyses/{analysis_id}/recommend")
def run_recommendations(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    a = db.query(AnalysisCase).filter(AnalysisCase.id == analysis_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Analysis not found")

    reqs = db.query(ExtractedRequirement).filter(ExtractedRequirement.analysis_id == analysis_id).all()
    if not reqs:
        raise HTTPException(status_code=400, detail="No requirements found for this analysis.")

    # Clear old recommendations & mappings
    db.query(RequirementStandardMapping).filter(RequirementStandardMapping.analysis_id == analysis_id).delete()
    db.query(Recommendation).filter(Recommendation.analysis_id == analysis_id).delete()
    db.flush()

    standards = db.query(StandardCatalogue).all()
    scored = []
    for std in standards:
        rec_dict, mappings = compute_recommendation(reqs, std, analysis_category=a.category)
        scored.append((rec_dict, mappings))

    scored.sort(key=lambda x: x[0]["relevance_score"], reverse=True)
    top_results = scored[:6]

    for rec_dict, mappings in top_results:
        rec = Recommendation(analysis_id=analysis_id, **rec_dict)
        db.add(rec)
        for m in mappings:
            db.add(RequirementStandardMapping(analysis_id=analysis_id, **m))

    a.status = "completed"
    a.progress_step = 7

    db.add(AuditEvent(
        user_id=current_user.id,
        username=current_user.username,
        action="GENERATE_RECOMMENDATIONS",
        entity_type="analysis",
        entity_id=str(analysis_id),
        details=f"Generated {len(top_results)} ranked recommendations.",
    ))
    db.commit()
    return {"message": "Recommendations generated", "count": len(top_results)}


@router.get("/analyses/{analysis_id}/recommendations")
def get_recommendations(analysis_id: int, db: Session = Depends(get_db)):
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.analysis_id == analysis_id)
        .order_by(Recommendation.relevance_score.desc())
        .all()
    )
    out = []
    for r in recs:
        std = r.standard
        out.append({
            "id": r.id,
            "analysis_id": r.analysis_id,
            "relevance_score": r.relevance_score,
            "match_label": r.match_label,
            "score_breakdown": r.score_breakdown,
            "explanation": r.explanation,
            "addressed_req_codes": r.addressed_req_codes,
            "unaddressed_req_codes": r.unaddressed_req_codes,
            "matching_concepts": r.matching_concepts,
            "tender_evidence": r.tender_evidence,
            "catalogue_evidence": r.catalogue_evidence,
            "uncertainty_notes": r.uncertainty_notes,
            "recommended_action": r.recommended_action,
            "standard": {
                "id": std.id,
                "catalogue_id": std.catalogue_id,
                "title": std.title,
                "sector": std.sector,
                "product_category": std.product_category,
                "verification_status": std.verification_status,
                "version_info": std.version_info,
                "qco_status": std.qco_status,
                "source_provenance": std.source_provenance,
            },
            "decision": {
                "decision": r.decision.decision,
                "comments": r.decision.comments,
                "decided_at": r.decision.decided_at.isoformat() if r.decision.decided_at else None,
            } if r.decision else None,
        })
    return out


@router.post("/recommendations/{rec_id}/decision")
def save_decision(
    rec_id: int,
    payload: DecisionIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    existing = db.query(ReviewerDecision).filter(ReviewerDecision.recommendation_id == rec_id).first()
    if existing:
        existing.decision = payload.decision
        existing.comments = payload.comments or ""
        existing.decided_by_id = current_user.id
    else:
        db.add(ReviewerDecision(
            recommendation_id=rec_id,
            decision=payload.decision,
            comments=payload.comments or "",
            decided_by_id=current_user.id,
        ))

    db.add(AuditEvent(
        user_id=current_user.id,
        username=current_user.username,
        action="REVIEWER_DECISION",
        entity_type="recommendation",
        entity_id=str(rec_id),
        details=f"Marked recommendation {rec_id} as '{payload.decision}'",
    ))
    db.commit()
    return {"message": "Decision saved", "decision": payload.decision}


@router.get("/analyses/{analysis_id}/coverage")
def get_coverage_matrix(analysis_id: int, db: Session = Depends(get_db)):
    reqs = (
        db.query(ExtractedRequirement)
        .filter(ExtractedRequirement.analysis_id == analysis_id)
        .order_by(ExtractedRequirement.id.asc())
        .all()
    )
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.analysis_id == analysis_id)
        .order_by(Recommendation.relevance_score.desc())
        .all()
    )
    mappings = (
        db.query(RequirementStandardMapping)
        .filter(RequirementStandardMapping.analysis_id == analysis_id)
        .all()
    )
    map_lookup = {(m.requirement_id, m.standard_id): m for m in mappings}

    columns = [
        {
            "standard_id": r.standard.id,
            "catalogue_id": r.standard.catalogue_id,
            "title": r.standard.title,
            "relevance_score": r.relevance_score,
        }
        for r in recs
    ]

    rows = []
    uncovered_critical = []
    for req in reqs:
        cells = []
        any_covered = False
        for r in recs:
            m = map_lookup.get((req.id, r.standard.id))
            status = m.coverage_status if m else "not_covered"
            if status in ("covered", "partially_covered"):
                any_covered = True
            cells.append({
                "standard_id": r.standard.id,
                "catalogue_id": r.standard.catalogue_id,
                "coverage_status": status,
                "evidence_note": m.evidence_note if m else "",
                "confidence": m.confidence if m else 0.0,
            })
        if not any_covered and req.criticality == "critical":
            uncovered_critical.append({
                "req_code": req.req_code,
                "description": req.description,
                "category": req.category,
            })
        rows.append({
            "requirement_id": req.id,
            "req_code": req.req_code,
            "description": req.description,
            "category": req.category,
            "criticality": req.criticality,
            "cells": cells,
        })

    return {
        "columns": columns,
        "rows": rows,
        "uncovered_critical": uncovered_critical,
    }

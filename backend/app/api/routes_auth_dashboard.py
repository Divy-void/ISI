from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.auth import get_current_user
from app.models.models import (
    User,
    AnalysisCase,
    Recommendation,
    SavedStandard,
    StandardCatalogue,
    AuditEvent,
)
from app.schemas.schemas import DemoLoginRequest

router = APIRouter(prefix="/api", tags=["auth-dashboard"])


@router.get("/health")
def health_check():
    return {"status": "ok", "app": "IS-Assist", "environment": "demo"}


@router.post("/auth/demo-login")
def demo_login(payload: DemoLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.role == payload.role, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Demo role '{payload.role}' not found.")
    db.add(AuditEvent(
        user_id=user.id,
        username=user.username,
        action="DEMO_LOGIN",
        entity_type="user",
        entity_id=str(user.id),
        details=f"Signed in as {user.role}",
    ))
    db.commit()
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "department_name": user.department.name if user.department else "General",
        "demo_notice": "Demo authentication active. Not for production use.",
    }


@router.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "department_name": current_user.department.name if current_user.department else "General",
    }


@router.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(AuditEvent(
        user_id=current_user.id,
        username=current_user.username,
        action="DEMO_LOGOUT",
        entity_type="user",
        entity_id=str(current_user.id),
        details="User signed out of demo session.",
    ))
    db.commit()
    return {"message": "Logged out"}


@router.get("/dashboard/stats")
def dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_documents = db.query(AnalysisCase).count()
    standards_identified = db.query(Recommendation).count()
    awaiting_review = db.query(AnalysisCase).filter(AnalysisCase.status == "awaiting_review").count()
    saved_standards = db.query(SavedStandard).filter(SavedStandard.user_id == current_user.id).count()
    catalogue_count = db.query(StandardCatalogue).count()

    return {
        "total_documents_processed": total_documents,
        "standards_identified": standards_identified,
        "analyses_awaiting_review": awaiting_review,
        "saved_standards": saved_standards,
        "catalogue_count": catalogue_count,
    }


@router.get("/dashboard/recent")
def dashboard_recent(db: Session = Depends(get_db)):
    recent_analyses = (
        db.query(AnalysisCase)
        .order_by(AnalysisCase.created_at.desc())
        .limit(5)
        .all()
    )
    recent_audit = (
        db.query(AuditEvent)
        .order_by(AuditEvent.created_at.desc())
        .limit(6)
        .all()
    )
    latest_catalogue = (
        db.query(StandardCatalogue)
        .order_by(StandardCatalogue.updated_at.desc())
        .limit(4)
        .all()
    )
    return {
        "recent_analyses": [
            {
                "id": a.id,
                "title": a.title,
                "category": a.category,
                "department_name": a.department_name,
                "status": a.status,
                "is_sample": a.is_sample,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in recent_analyses
        ],
        "recent_activity": [
            {
                "id": e.id,
                "username": e.username,
                "action": e.action,
                "details": e.details,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in recent_audit
        ],
        "latest_catalogue_updates": [
            {
                "id": s.id,
                "catalogue_id": s.catalogue_id,
                "title": s.title,
                "sector": s.sector,
                "verification_status": s.verification_status,
            }
            for s in latest_catalogue
        ],
    }

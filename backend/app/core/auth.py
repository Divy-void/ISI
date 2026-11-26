from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User


def get_current_user(
    x_demo_role: str = Header(default="procurement_officer"),
    db: Session = Depends(get_db),
) -> User:
    """
    Demo authentication resolver using X-Demo-Role header.
    Not for production use.
    """
    user = db.query(User).filter(User.role == x_demo_role, User.is_active == True).first()
    if not user:
        user = db.query(User).filter(User.role == "procurement_officer").first()
    if not user:
        raise HTTPException(status_code=401, detail="Demo user not found")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator role required for this action.")
    return current_user

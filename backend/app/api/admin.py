from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from backend.app.database import get_db
from backend.app.core.deps import require_role
from backend.app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


class UserItem(BaseModel):
    id: str
    name: str
    email: str
    role: str
    location: str | None = None

    model_config = {"from_attributes": True}


class RoleUpdate(BaseModel):
    role: str


@router.get("/users", response_model=List[UserItem])
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    return db.query(User).order_by(User.name).all()


@router.patch("/users/{user_id}", response_model=UserItem)
def update_user_role(
    user_id: str,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    if payload.role not in ("recruiter", "admin", "student"):
        raise HTTPException(400, "Invalid role")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()
    return {"status": "deleted"}
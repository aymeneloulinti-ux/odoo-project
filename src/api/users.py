from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import UserOut, UserUpdate
from api.auth import get_current_active_user, get_password_hash, require_permission
from models.user import User
from services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    return user_service.get_user_by_id(user_id, db)


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    password_hash = get_password_hash(payload.password) if payload.password is not None else None
    return user_service.update_user(user_id, payload, db, password_hash=password_hash)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    return user_service.delete_user(user_id, db)

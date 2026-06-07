from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import RoleOut
from api.auth import require_permission
from models.user import User
from services import role_service

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    return role_service.list_roles(db)


@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    return role_service.get_role(role_id, db)

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import PermissionOut
from api.auth import require_permission
from models.user import User
from services import permission_service

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("/", response_model=list[PermissionOut])
def list_permissions(db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    return permission_service.list_permissions(db)


@router.get("/{permission_id}", response_model=PermissionOut)
def get_permission(permission_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_users"))):
    return permission_service.get_permission(permission_id, db)

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.permission import Permission


def list_permissions(db: Session) -> list[Permission]:
    stmt = select(Permission)
    return db.execute(stmt).scalars().all()


def get_permission(permission_id: int, db: Session) -> Permission:
    stmt = select(Permission).filter_by(id=permission_id)
    p = db.execute(stmt).scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Permission not found")
    return p

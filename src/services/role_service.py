from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.role import Role


def list_roles(db: Session) -> list[Role]:
    stmt = select(Role)
    return db.execute(stmt).scalars().all()


def get_role(role_id: int, db: Session) -> Role:
    stmt = select(Role).filter_by(id=role_id)
    r = db.execute(stmt).scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    return r

from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.user import User
from models.role import Role


def list_users(db: Session) -> list[User]:
    stmt = select(User)
    return db.execute(stmt).scalars().all()


def get_user_by_id(user_id: int, db: Session) -> User:
    stmt = select(User).filter_by(id=user_id)
    u = db.execute(stmt).scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u


def update_user(user_id: int, payload, db: Session, password_hash: str | None = None) -> User:
    u = get_user_by_id(user_id, db)
    if payload.username is not None:
        u.username = payload.username
    if password_hash is not None:
        u.password_ash = password_hash
    if payload.is_active is not None:
        u.is_active = payload.is_active
    if payload.role_id is not None:
        stmt = select(Role).filter_by(id=payload.role_id)
        role = db.execute(stmt).scalars().first()
        if not role:
            raise HTTPException(status_code=400, detail="Role not found")
        u.role = role
        u.role_id = role.id
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def delete_user(user_id: int, db: Session) -> None:
    u = get_user_by_id(user_id, db)
    db.delete(u)
    db.commit()
    return None


def create_user(username: str, password_hash: str, role_id: int, db: Session) -> User:
    stmt = select(Role).filter_by(id=role_id)
    role = db.execute(stmt).scalars().first()
    if not role:
        raise HTTPException(status_code=400, detail="Role not found")
    today = date.today()
    user = User(
        username=username,
        password_ash=password_hash,
        is_active=True,
        updated_at=today,
        created_at=today,
        role=role,
        role_id=role.id,
        stock_movements=[],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

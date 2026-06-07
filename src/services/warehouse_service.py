from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.warehouse import Warehouse


def list_warehouses(db: Session) -> list[Warehouse]:
    stmt = select(Warehouse)
    return db.execute(stmt).scalars().all()


def get_warehouse(warehouse_id: int, db: Session) -> Warehouse:
    stmt = select(Warehouse).filter_by(id=warehouse_id)
    w = db.execute(stmt).scalars().first()
    if not w:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return w


def create_warehouse(payload, db: Session) -> Warehouse:
    existing = db.execute(select(Warehouse).filter_by(name=payload.name)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Warehouse with this name already exists")
    w = Warehouse(name=payload.name, location=payload.location)
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def update_warehouse(warehouse_id: int, payload, db: Session) -> Warehouse:
    w = get_warehouse(warehouse_id, db)
    if payload.name is not None:
        w.name = payload.name
    if payload.location is not None:
        w.location = payload.location
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def delete_warehouse(warehouse_id: int, db: Session) -> None:
    w = get_warehouse(warehouse_id, db)
    db.delete(w)
    db.commit()
    return None

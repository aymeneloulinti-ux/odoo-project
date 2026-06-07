from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.stock_movement import StockMovement
from models.product import Product
from models.warehouse import Warehouse
from models.user import User


def list_movements(db: Session) -> list[StockMovement]:
    stmt = select(StockMovement)
    return db.execute(stmt).scalars().all()


def get_movement(movement_id: int, db: Session) -> StockMovement:
    stmt = select(StockMovement).filter_by(id=movement_id)
    sm = db.execute(stmt).scalars().first()
    if not sm:
        raise HTTPException(status_code=404, detail="Stock movement not found")
    return sm


def create_movement(payload, db: Session) -> StockMovement:
    prod = db.execute(select(Product).filter_by(id=payload.product_id)).scalars().first()
    if not prod:
        raise HTTPException(status_code=400, detail="Product not found")
    wh = db.execute(select(Warehouse).filter_by(id=payload.warehouse_id)).scalars().first()
    if not wh:
        raise HTTPException(status_code=400, detail="Warehouse not found")
    usr = db.execute(select(User).filter_by(id=payload.user_id)).scalars().first()
    if not usr:
        raise HTTPException(status_code=400, detail="User not found")

    price = payload.price if getattr(payload, "price", None) is not None else (
        prod.unit_price if payload.type == "OUT" else 0.0
    )

    sm = StockMovement(
        product_id=prod.id,
        warehouse_id=wh.id,
        user_id=usr.id,
        quantity=payload.quantity,
        price=price,
        type=payload.type,
        source_module=payload.source_module,
        reason=payload.reason,
    )
    db.add(sm)
    db.commit()
    db.refresh(sm)
    return sm


def delete_movement(movement_id: int, db: Session) -> None:
    sm = get_movement(movement_id, db)
    db.delete(sm)
    db.commit()
    return None

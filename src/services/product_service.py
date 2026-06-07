from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.product import Product
from models.category import Category


def list_products(db: Session) -> list[Product]:
    stmt = select(Product)
    return db.execute(stmt).scalars().all()


def get_product(product_id: int, db: Session) -> Product:
    stmt = select(Product).filter_by(id=product_id)
    prod = db.execute(stmt).scalars().first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod


def create_product(payload, db: Session) -> Product:
    cat = db.execute(select(Category).filter_by(id=payload.category_id)).scalars().first()
    if not cat:
        raise HTTPException(status_code=400, detail="Category not found")

    prod = Product(name=payload.name, unit_price=payload.unit_price, category_id=payload.category_id, category=cat, stock_movements=[])
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod


def update_product(product_id: int, payload, db: Session) -> Product:
    prod = get_product(product_id, db)

    if payload.name is not None:
        prod.name = payload.name
    if payload.unit_price is not None:
        prod.unit_price = payload.unit_price
    if payload.category_id is not None:
        cat = db.execute(select(Category).filter_by(id=payload.category_id)).scalars().first()
        if not cat:
            raise HTTPException(status_code=400, detail="Category not found")
        prod.category_id = payload.category_id
        prod.category = cat

    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod


def delete_product(product_id: int, db: Session) -> None:
    prod = get_product(product_id, db)
    db.delete(prod)
    db.commit()
    return None

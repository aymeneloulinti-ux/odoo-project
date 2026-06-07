from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.category import Category


def list_categories(db: Session) -> list[Category]:
    stmt = select(Category)
    return db.execute(stmt).scalars().all()


def get_category(category_id: int, db: Session) -> Category:
    stmt = select(Category).filter_by(id=category_id)
    cat = db.execute(stmt).scalars().first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


def create_category(payload, db: Session) -> Category:
    existing = db.execute(select(Category).filter_by(name=payload.name)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    c = Category(name=payload.name, location=payload.location, products=[])
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def update_category(category_id: int, payload, db: Session) -> Category:
    cat = get_category(category_id, db)
    if payload.name is not None:
        cat.name = payload.name
    if payload.location is not None:
        cat.location = payload.location
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def delete_category(category_id: int, db: Session) -> None:
    cat = get_category(category_id, db)
    db.delete(cat)
    db.commit()
    return None

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import ProductCreate, ProductOut, ProductUpdate
from api.auth import get_current_active_user, require_permission
from models.user import User
from services import product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), current_user: User = Depends(require_permission("read_product"))):
    return product_service.list_products(db)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("read_product"))):
    return product_service.get_product(product_id, db)


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("write_product"))):
    return product_service.create_product(payload, db)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("write_product"))):
    return product_service.update_product(product_id, payload, db)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("write_product"))):
    return product_service.delete_product(product_id, db)

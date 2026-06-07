from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import CategoryCreate, CategoryOut, CategoryUpdate
from api.auth import get_current_active_user
from models.user import User
from services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return category_service.list_categories(db)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return category_service.get_category(category_id, db)


@router.post("/", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return category_service.create_category(payload, db)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return category_service.update_category(category_id, payload, db)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return category_service.delete_category(category_id, db)

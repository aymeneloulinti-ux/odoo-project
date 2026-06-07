from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import StockMovementCreate, StockMovementOut
from api.auth import require_permission
from models.user import User
from services import stock_movement_service

router = APIRouter(prefix="/stock_movements", tags=["stock_movements"])


@router.get("/", response_model=list[StockMovementOut])
def list_movements(db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_stock"))):
    return stock_movement_service.list_movements(db)


@router.get("/{movement_id}", response_model=StockMovementOut)
def get_movement(movement_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_stock"))):
    return stock_movement_service.get_movement(movement_id, db)


@router.post("/", response_model=StockMovementOut, status_code=201)
def create_movement(payload: StockMovementCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_stock"))):
    return stock_movement_service.create_movement(payload, db)


@router.delete("/{movement_id}", status_code=204)
def delete_movement(movement_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_stock"))):
    return stock_movement_service.delete_movement(movement_id, db)

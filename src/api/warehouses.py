from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import WarehouseCreate, WarehouseOut, WarehouseUpdate
from api.auth import get_current_active_user
from models.user import User
from services import warehouse_service

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.get("/", response_model=list[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db)):
    return warehouse_service.list_warehouses(db)


@router.get("/{warehouse_id}", response_model=WarehouseOut)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    return warehouse_service.get_warehouse(warehouse_id, db)


@router.post("/", response_model=WarehouseOut, status_code=201)
def create_warehouse(payload: WarehouseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return warehouse_service.create_warehouse(payload, db)


@router.put("/{warehouse_id}", response_model=WarehouseOut)
def update_warehouse(warehouse_id: int, payload: WarehouseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return warehouse_service.update_warehouse(warehouse_id, payload, db)


@router.delete("/{warehouse_id}", status_code=204)
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return warehouse_service.delete_warehouse(warehouse_id, db)

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum


# Category schemas
class CategoryBase(BaseModel):
    name: str
    location: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    username: str
    is_active: bool = True
    role_id: int


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


# Auth token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Product schemas
class ProductBase(BaseModel):
    name: str
    unit_price: float
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    unit_price: Optional[float] = None
    category_id: Optional[int] = None


class ProductOut(ProductBase):
    id: int
    category: Optional[CategoryOut] = None

    class Config:
        from_attributes = True


# Role / Permission schemas
class RoleOut(BaseModel):
    id: int
    role_name: str

    class Config:
        from_attributes = True


class PermissionOut(BaseModel):
    id: int
    code: str

    class Config:
        from_attributes = True


# Warehouse schemas
class WarehouseBase(BaseModel):
    name: str
    location: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class WarehouseOut(WarehouseBase):
    id: int

    class Config:
        from_attributes = True


# Stock movement schemas
class StockMovementBase(BaseModel):
    product_id: int
    warehouse_id: int
    user_id: int
    quantity: int
    price: float
    type: str
    source_module: str
    reason: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    pass


class StockMovementOut(StockMovementBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# User update schema
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None

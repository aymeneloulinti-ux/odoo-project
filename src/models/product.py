from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from models.base import Base
if TYPE_CHECKING:
    from models.category import Category
    from models.stock_movement import StockMovement


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column()
    unit_price: Mapped[float] = mapped_column()
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped[Category] = relationship(
        "Category", back_populates="products")

    stock_movements: Mapped[list[StockMovement]] = relationship(
        "StockMovement", back_populates="product")

from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from models.base import Base
if TYPE_CHECKING:
    from models.stock_movement import StockMovement


class Warehouse(Base):
    __tablename__ = 'warehouses'
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(unique=True)
    location: Mapped[str | None] = mapped_column(nullable=True)

    stock_movements: Mapped[list[StockMovement]] = relationship(
        'StockMovement', back_populates='warehouse')

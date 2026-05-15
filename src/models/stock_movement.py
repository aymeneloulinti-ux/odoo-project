from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.product import Product
    from models.warehouse import Warehouse


class MovementType(Enum):
    IN = "IN"
    OUT = "OUT"


class SourceModule(Enum):
    MANUAL = "manual"
    PURCHASE = "purchase"
    SALES = "sales"
    INVOICE = "invoice"
    ADJUSTMENT = "adjustment"


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id")
    )

    quantity: Mapped[int] = mapped_column()

    type: Mapped[MovementType] = mapped_column(
        SqlEnum(MovementType)
    )

    source_module: Mapped[SourceModule] = mapped_column(
        SqlEnum(SourceModule)
    )

    reason: Mapped[str] = mapped_column(nullable=True)

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="stock_movements"
    )

    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse",
        back_populates="stock_movements"
    )

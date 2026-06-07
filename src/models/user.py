from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.stock_movement import StockMovement
    from models.role import Role    
    
class User(Base):
    __tablename__ ="users"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(nullable=False)
    password_ash: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)
    updated_at: Mapped[date] = mapped_column()
    created_at: Mapped[date] = mapped_column()
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    
    role: Mapped[Role] = relationship("Role", back_populates="users")
    stock_movements: Mapped[list[StockMovement]] = relationship("StockMovement", back_populates="user")
    
    
    



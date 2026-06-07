from __future__ import annotations

from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from models.role_permission_table import role_permission

if TYPE_CHECKING:
    from models.role import Role

class Permission(Base):
    __tablename__ = 'permissions'
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    code: Mapped[str] = mapped_column()
    
    roles: Mapped[List[Role]] = relationship("Role",secondary='role_permission', back_populates='permissions')
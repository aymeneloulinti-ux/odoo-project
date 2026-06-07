from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, List
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.user import User
    from models.permission import Permission
    
class RoleName(Enum):
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    WAREHOUSE = 'WAREHOUSE'
    
class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    role_name: Mapped[RoleName] = mapped_column(SqlEnum(RoleName))
    
    permissions : Mapped[List[Permission]] = relationship("Permission", secondary='role_permission', back_populates='roles')
    users: Mapped[List[User]] = relationship("User", back_populates='role')
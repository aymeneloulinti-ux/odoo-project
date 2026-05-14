from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from models.base import Base
if TYPE_CHECKING:
    from models.category import Category


class Product(Base):
    pass

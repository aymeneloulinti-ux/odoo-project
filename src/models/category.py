from models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.product import Product


class Category(Base):
    __tablename__ = 'category'
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()

    products: Mapped[list['Product']] = relationship(
        'Product', back_populates='category')

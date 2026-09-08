from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

if TYPE_CHECKING:
    from app.models.order import OrderItem


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product",
    )

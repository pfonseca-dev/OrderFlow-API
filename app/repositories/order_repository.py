from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.product import Product


class OrderRepository:
    def get_products_by_ids(
        self, db: Session, products_ids: list[int]
    ) -> list[Product]:
        statement = select(Product).where(Product.id.in_(products_ids))

        return list(db.scalars(statement).all())

    def create(self, db: Session, order: Order) -> Order:
        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    def list_all(self, db: Session) -> list[Order]:
        statement = select(Order).order_by(Order.id)

        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, order_id: int) -> Order | None:
        return db.get(Order, order_id)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate


class ProductRepository:
    def create(self, db: Session, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())

        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    def list_all(self, db: Session) -> list[Product]:
        statement = select(Product).order_by(Product.id)

        # repository
        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, product_id: int) -> Product | None:
        return db.get(Product, product_id)

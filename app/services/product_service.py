from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate


class ProductService:
    # service
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    def create(self, db: Session, product_data: ProductCreate) -> Product:
        return self.repository.create(db, product_data)

    def list_all(self, db: Session) -> list[Product]:
        return self.repository.list_all(db)

    def get_by_id(self, db: Session, product_id: int) -> Product:
        product = self.repository.get_by_id(db, product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        return product

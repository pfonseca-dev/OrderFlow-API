from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

repositories = ProductRepository()
service = ProductService(repositories)

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(db: DbSession, product_data: ProductCreate) -> ProductResponse:
    product = service.create(db, product_data)

    return ProductResponse.model_validate(product)


@router.get(
    "",
    response_model=list[ProductResponse],
)
def list_products(
    db: DbSession,
) -> list[ProductResponse]:
    products = service.list_all(db)

    return [ProductResponse.model_validate(product) for product in products]


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(db: DbSession, product_id: int) -> ProductResponse:
    product = service.get_by_id(db, product_id)

    return ProductResponse.model_validate(product)

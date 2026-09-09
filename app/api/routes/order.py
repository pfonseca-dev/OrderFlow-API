from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse
from app.services.delivery_service import DeliveryService
from app.services.order_service import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

repository = OrderRepository()
delivery_service = DeliveryService()
service = OrderService(repository, delivery_service)

DbSession = Annotated[Session, Depends(get_db)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
def create(db: DbSession, order_data: OrderCreate) -> OrderResponse:
    return service.create(db, order_data)

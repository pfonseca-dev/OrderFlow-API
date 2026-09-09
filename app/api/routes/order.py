from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
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


@router.get("", response_model=list[OrderResponse])
def list_orders(db: DbSession) -> list[OrderResponse]:
    return service.list(db)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(db: DbSession, order_id: int) -> OrderResponse:
    return service.get_by_id(db, order_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    db: DbSession, order_id: int, status_data: OrderStatusUpdate
) -> OrderResponse:
    return service.update_status(db, order_id, status_data.status)

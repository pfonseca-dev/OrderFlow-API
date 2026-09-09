from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderItemResponse, OrderResponse
from app.services.delivery_service import DeliveryService


class OrderService:
    def __init__(self, repository: OrderRepository, delivery: DeliveryService) -> None:
        self.repository = repository
        self.delivery = delivery

    def create(self, db: Session, order_data: OrderCreate) -> OrderResponse:
        product_ids = [item.product_id for item in order_data.items]

        products = self.repository.get_products_by_ids(db, product_ids)

        product_by_id = {product.id: product for product in products}

        self._validate_products(product_ids, product_by_id)

        delivery_distance = self.delivery.calculate_distance(
            original_latitude=Decimal(str(settings.restaurant_latitude)),
            original_longitude=Decimal(str(settings.restaurant_longitude)),
            destination_latitude=order_data.delivery.latitude,
            destination_longitude=order_data.delivery.longitude,
        )

        delivery_fee = self.delivery.calculate_fee(delivery_distance)

        order = Order(
            delivery_latitude=order_data.delivery.latitude,
            delivery_longitude=order_data.delivery.longitude,
            delivery_distance_km=delivery_distance,
            delivery_fee=delivery_fee,
        )

        for item_data in order_data.items:
            product = product_by_id[item_data.product_id]
            unit_price = product.price

            order_item = OrderItem(
                product_id=product.id,
                quantity=item_data.quantity,
                unit_price=unit_price,
            )

            order.items.append(order_item)

        order = self.repository.create(db, order)

        return self._to_response(order)

    def _validate_products(
        self, product_ids: list[int], products_by_id: dict[int, Product]
    ) -> None:
        for product_id in product_ids:
            product = products_by_id.get(product_id)

            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {product_id} not found",
                )

            if not product.is_available:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {product_id} is not available",
                )

    def _to_response(self, order: Order) -> OrderResponse:
        response_items: list[OrderItemResponse] = []
        subtotal = Decimal("0.00")

        for item in order.items:
            item_subtotal = item.unit_price * item.quantity

            response_items.append(
                OrderItemResponse(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item_subtotal,
                )
            )

            subtotal += item_subtotal

        total = subtotal + order.delivery_fee

        return OrderResponse(
            id=order.id,
            status=OrderStatus(order.status),
            items=response_items,
            subtotal=subtotal,
            delivery_distance_km=order.delivery_distance_km,
            delivery_fee=order.delivery_fee,
            total=total,
        )

    def list(self, db: Session) -> list[OrderResponse]:
        orders = self.repository.list_all(db)

        return [self._to_response(order) for order in orders]

    def get_by_id(self, db: Session, order_id: int) -> OrderResponse:
        order = self.repository.get_by_id(db, order_id)

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found",
            )
        return self._to_response(order)

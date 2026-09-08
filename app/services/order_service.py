from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderItemResponse, OrderResponse


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    def create(self, db: Session, order_data: OrderCreate) -> OrderResponse:
        product_ids = [item.product_id for item in order_data.items]

        products = self.repository.get_products_by_ids(db, product_ids)

        product_by_id = {product.id: product for product in products}

        self._validate_products(product_ids, product_by_id)

        order = Order()

        response_items: list[OrderItemResponse] = []
        total = Decimal("0.00")

        for item_data in order_data.items:
            product = product_by_id[item_data.product_id]

            unit_price = product.price
            subtotal = unit_price * item_data.quantity

            order_item = OrderItem(
                product_id=product.id,
                quantity=item_data.quantity,
                unit_price=unit_price,
            )

            order.items.append(order_item)

            response_items.append(
                OrderItemResponse(
                    product_id=product.id,
                    quantity=item_data.quantity,
                    unit_price=unit_price,
                    subtotal=subtotal,
                )
            )

            total += subtotal

        order = self.repository.create(db, order)

        return OrderResponse(
            id=order.id,
            status=OrderStatus(order.status),
            items=response_items,
            subtotal=total,
            total=total,
        )

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

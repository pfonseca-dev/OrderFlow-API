from decimal import Decimal

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product


def test_orders_has_pending_status_by_default() -> None:
    order = Order()

    assert order.status == OrderStatus.PENDING.value


def test_order_can_have_multiple_items() -> None:
    product_one = Product(
        name="Hamburger",
        description="Hamburger artesanal",
        price=Decimal("25.90"),
        is_available=True,
    )

    product_two = Product(
        name="Batata",
        description="Batata frita",
        price=Decimal("12.00"),
        is_available=True,
    )

    order = Order()

    item_one = OrderItem(
        product=product_one,
        quantity=2,
        unit_price=Decimal("25.90"),
    )

    item_two = OrderItem(
        product=product_two,
        quantity=1,
        unit_price=Decimal("12.00"),
    )

    order.items = [item_one, item_two]

    assert len(order.items) == 2
    assert order.items[0].quantity == 2
    assert order.items[0].unit_price == Decimal("25.90")
    assert order.items[0].product is product_one
    assert order.items[1].product is product_two

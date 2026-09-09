from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.order import OrderItemCreate
from app.services.delivery_service import DeliveryService

client = TestClient(app)


def create_product(name: str, price: str, is_available: bool = True) -> int:
    response = client.post(
        "/api/products",
        json={
            "name": name,
            "description": f"{name} description",
            "price": price,
            "is_available": is_available,
        },
    )

    assert response.status_code == 201

    data = response.json()
    product_id = data["id"]

    assert isinstance(product_id, int)

    return product_id


def test_create_order_with_multiple_items_and_delivery() -> None:
    hamburger_id = create_product(
        "Order Test Hamburger",
        "25.90",
    )
    fries_id = create_product(
        "Order Test Fries",
        "12.00",
    )

    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": hamburger_id,
                    "quantity": 2,
                },
                {
                    "product_id": fries_id,
                    "quantity": 1,
                },
            ],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-45.1300",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["status"] == "pending"

    assert len(data["items"]) == 2

    assert Decimal(data["items"][0]["unit_price"]) == Decimal("25.90")
    assert Decimal(data["items"][0]["subtotal"]) == Decimal("51.80")

    assert Decimal(data["items"][1]["unit_price"]) == Decimal("12.00")
    assert Decimal(data["items"][1]["subtotal"]) == Decimal("12.00")

    assert Decimal(data["subtotal"]) == Decimal("63.80")

    delivery_distance = Decimal(data["delivery_distance_km"])
    delivery_fee = Decimal(data["delivery_fee"])
    total = Decimal(data["total"])

    assert delivery_distance > Decimal("0.00")
    assert delivery_fee > Decimal("0.00")
    assert total == Decimal("63.80") + delivery_fee


def test_create_order_with_product_not_found() -> None:
    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": 999999,
                    "quantity": 1,
                }
            ],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-45.1300",
            },
        },
    )

    assert response.status_code == 404


def test_create_order_with_unavailable_product() -> None:
    product_id = create_product(
        "Unavailable Order Test Product",
        "10.00",
        is_available=False,
    )

    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                }
            ],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-45.1300",
            },
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": f"Product {product_id} is not available",
    }


def test_create_order_with_zero_quantity() -> None:
    product_id = create_product("Zero Quantity Product", "10.00")

    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 0,
                }
            ],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-45.1300",
            },
        },
    )

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert len(errors) == 1
    assert errors[0]["loc"] == ["body", "items", 0, "quantity"]
    assert errors[0]["type"] == "greater_than"


def test_create_order_with_negative_quantity() -> None:
    product_id = create_product("Negative Quantity Product", "10.00")

    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": -1,
                }
            ],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-45.1300",
            },
        },
    )

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert len(errors) == 1
    assert errors[0]["loc"] == ["body", "items", 0, "quantity"]
    assert errors[0]["type"] == "greater_than"


def test_create_order_with_quantity_above_integer_limit() -> None:
    product_id = create_product("Quantity Above Integer Limit Product", "10.00")

    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2147483648,
                }
            ],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-45.1300",
            },
        },
    )

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert len(errors) == 1
    assert errors[0]["loc"] == ["body", "items", 0, "quantity"]
    assert errors[0]["type"] == "less_than_equal"
    assert errors[0]["ctx"]["le"] == 2147483647


def test_order_item_accepts_maximum_quantity() -> None:
    item = OrderItemCreate(product_id=1, quantity=2147483647)

    assert item.quantity == 2147483647


def test_create_order_with_empty_items() -> None:
    response = client.post(
        "/api/orders",
        json={
            "items": [],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-45.1300",
            },
        },
    )

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert len(errors) == 1
    assert errors[0]["loc"] == ["body", "items"]
    assert errors[0]["type"] == "too_short"


def test_create_order_with_invalid_latitude() -> None:
    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                }
            ],
            "delivery": {
                "latitude": "100.00",
                "longitude": "-45.1300",
            },
        },
    )

    assert response.status_code == 422


def test_create_order_with_invalid_longitude() -> None:
    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                }
            ],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-200.00",
            },
        },
    )

    assert response.status_code == 422


def test_delivery_fee_changes_by_distance() -> None:
    service = DeliveryService()

    assert service.calculate_fee(Decimal("1.50")) == Decimal("5.00")
    assert service.calculate_fee(Decimal("3.00")) == Decimal("8.00")
    assert service.calculate_fee(Decimal("7.00")) == Decimal("12.00")
    assert service.calculate_fee(Decimal("15.00")) == Decimal("18.00")


def test_delivery_distance_is_zero_for_same_location() -> None:
    service = DeliveryService()

    distance = service.calculate_distance(
        original_latitude=Decimal("-22.7300"),
        original_longitude=Decimal("-45.1200"),
        destination_latitude=Decimal("-22.7300"),
        destination_longitude=Decimal("-45.1200"),
    )

    assert distance == Decimal("0.00")


def test_list_orders() -> None:
    product_id = create_product(
        "List Orders Product",
        "20.00",
    )

    create_response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                }
            ],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-45.1300",
            },
        },
    )

    assert create_response.status_code == 201

    response = client.get("/api/orders")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    order = data[-1]

    assert order["status"] == "pending"
    assert len(order["items"]) == 1

    assert Decimal(order["items"][0]["unit_price"]) == Decimal("20.00")
    assert Decimal(order["items"][0]["subtotal"]) == Decimal("40.00")

    assert Decimal(order["subtotal"]) == Decimal("40.00")
    assert Decimal(order["delivery_fee"]) > Decimal("0.00")
    assert Decimal(order["total"]) == (
        Decimal(order["subtotal"]) + Decimal(order["delivery_fee"])
    )


def test_get_order_by_id() -> None:
    product_id = create_product(
        "Get Order Product",
        "15.50",
    )

    create_response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                }
            ],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-45.1300",
            },
        },
    )

    assert create_response.status_code == 201

    created_order = create_response.json()
    order_id = created_order["id"]

    response = client.get(f"/api/orders/{order_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == order_id
    assert data["status"] == "pending"

    assert len(data["items"]) == 1

    assert data["items"][0]["product_id"] == product_id
    assert data["items"][0]["quantity"] == 2
    assert Decimal(data["items"][0]["unit_price"]) == Decimal("15.50")
    assert Decimal(data["items"][0]["subtotal"]) == Decimal("31.00")

    assert Decimal(data["subtotal"]) == Decimal("31.00")
    assert Decimal(data["delivery_fee"]) > Decimal("0.00")
    assert Decimal(data["total"]) == (
        Decimal(data["subtotal"]) + Decimal(data["delivery_fee"])
    )


def create_order_for_status_test() -> int:
    product_id = create_product(
        "Status Test Product",
        "20.00",
    )

    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                }
            ],
            "delivery": {
                "latitude": "-22.7500",
                "longitude": "-45.1300",
            },
        },
    )

    assert response.status_code == 201

    order_id = response.json()["id"]

    assert isinstance(order_id, int)

    return order_id


def test_update_order_status_through_full_lifecycle() -> None:
    order_id = create_order_for_status_test()

    transitions = [
        "confirmed",
        "preparing",
        "out_of_delivery",
        "delivered",
    ]

    for new_status in transitions:
        response = client.patch(
            f"/api/orders/{order_id}/status",
            json={"status": new_status},
        )

        assert response.status_code == 200
        assert response.json()["status"] == new_status

    response = client.get(f"/api/orders/{order_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "delivered"


def test_cancel_pending_order() -> None:
    order_id = create_order_for_status_test()

    response = client.patch(
        f"/api/orders/{order_id}/status",
        json={"status": "cancelled"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_reject_invalid_order_status_transition() -> None:
    order_id = create_order_for_status_test()

    response = client.patch(
        f"/api/orders/{order_id}/status",
        json={"status": "delivered"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid status transition: pending -> delivered",
    }


def test_update_status_order_not_found() -> None:
    response = client.patch(
        "/api/orders/999999/status",
        json={"status": "confirmed"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Order 999999 not found",
    }


def test_reject_invalid_order_status() -> None:
    order_id = create_order_for_status_test()

    response = client.patch(
        f"/api/orders/{order_id}/status",
        json={"status": "banana"},
    )

    assert response.status_code == 422


def test_delivered_order_cannot_change_status() -> None:
    order_id = create_order_for_status_test()

    for new_status in [
        "confirmed",
        "preparing",
        "out_of_delivery",
        "delivered",
    ]:
        response = client.patch(
            f"/api/orders/{order_id}/status",
            json={"status": new_status},
        )

        assert response.status_code == 200

    response = client.patch(
        f"/api/orders/{order_id}/status",
        json={"status": "preparing"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid status transition: delivered -> preparing",
    }
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid status transition: delivered -> preparing",
    }

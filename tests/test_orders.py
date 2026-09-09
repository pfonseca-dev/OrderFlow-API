from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
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
    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 0,
                }
            ]
        },
    )

    assert response.status_code == 422


def test_create_order_with_negative_quantity() -> None:
    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": -1,
                }
            ]
        },
    )

    assert response.status_code == 422


def test_create_order_with_empty_items() -> None:
    response = client.post(
        "/api/orders",
        json={
            "items": [],
        },
    )

    assert response.status_code == 422


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

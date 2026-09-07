from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_product() -> None:
    response = client.post(
        "/api/products",
        json={
            "name": "Hambúrguer Clássico",
            "description": "Pão, carne, queijo e molho",
            "price": "29.90",
            "is_available": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "Hambúrguer Clássico"
    assert data["description"] == "Pão, carne, queijo e molho"
    assert Decimal(data["price"]) == Decimal("29.90")
    assert data["is_available"] is True


def test_list_products() -> None:
    response = client.get("/api/products")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_product_by_id() -> None:
    create_response = client.post(
        "/api/products",
        json={
            "name": "Coca-Cola",
            "description": "Refrigerante lata",
            "price": "7.50",
            "is_available": True,
        },
    )

    product_id = create_response.json()["id"]

    response = client.get(f"/api/products/{product_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Coca-Cola"


def test_get_product_not_found() -> None:
    response = client.get("/api/products/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found",
    }


def test_create_product_with_invalid_price() -> None:
    response = client.post(
        "/api/products",
        json={
            "name": "Produto inválido",
            "description": None,
            "price": "-10.00",
            "is_available": True,
        },
    )

    assert response.status_code == 422

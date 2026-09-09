from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class DeliveryLocation(BaseModel):
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)
    delivery: DeliveryLocation


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    items: list[OrderItemResponse]
    subtotal: Decimal
    delivery_distance_km: Decimal
    delivery_fee: Decimal
    total: Decimal


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

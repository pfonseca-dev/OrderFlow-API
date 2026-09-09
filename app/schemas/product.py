from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    description: str | None = Field(min_length=1, max_length=500)

    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

    is_available: bool = True


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    is_available: bool

    model_config = ConfigDict(from_attributes=True)

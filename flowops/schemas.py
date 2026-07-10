from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber

from flowops.models import ProductTag, UnitOfMeasure


class IngredientSchema(BaseModel):
    name: str
    unit_of_measure: UnitOfMeasure
    minimum: Decimal
    quantity: Decimal


class IngredientPublic(IngredientSchema):
    id: int


class IngredientList(BaseModel):
    ingredients: list[IngredientPublic]


class IngredientUpdate(BaseModel):
    name: str | None = None
    unit_of_measure: UnitOfMeasure | None = None
    minimum: Decimal | None = None
    quantity: Decimal | None = None


class ProductSchema(BaseModel):
    name: str
    description: str
    preparation_time: int
    price: Decimal
    ingredients_quantity: dict
    tag: ProductTag


class ProductPublic(BaseModel):
    name: str
    description: str
    preparation_time: int
    price: Decimal
    tag: ProductTag
    id: int


class ProductList(BaseModel):
    products: list[ProductPublic]


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    preparation_time: int | None = None
    price: Decimal | None = None
    tag: ProductTag | None = None


class UserSchema(BaseModel):
    name: str
    phone: PhoneNumber
    address: str | None = None


class UserPublic(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[UserPublic]


class UserUpdate(BaseModel):
    name: str | None = None
    phone: PhoneNumber | None = None
    address: str | None = None


class OrderSchema(BaseModel):
    client_id: int
    notes: str
    product_quantity: dict


class OrderPublic(BaseModel):
    id: int
    ordered_at: datetime
    notes: str
    final_amount: Decimal
    estimated_ready_at: datetime


class OrderList(BaseModel):
    orders: list[OrderPublic]


class OrderUpdate(BaseModel):
    client_id: int | None = None
    ordered_at: datetime | None = None
    notes: str | None = None
    product_quantity: dict | None = None

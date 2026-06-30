from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber

from flowops.models import UnitOfMeasure


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
    ingredients_quantity: dict


class ProductPublic(BaseModel):
    name: str
    description: str
    preparation_time: int
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    products: list[ProductPublic]


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    preparation_time: int | None = None


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

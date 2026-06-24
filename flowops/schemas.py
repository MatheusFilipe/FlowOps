from decimal import Decimal

from pydantic import BaseModel

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

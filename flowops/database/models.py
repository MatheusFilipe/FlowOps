from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column, registry

table_registry = registry()


@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    phone: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]


@mapped_as_dataclass(table_registry)
class Product:
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[float]
    preparation_time: Mapped[int]  # minutes
    ingredients: Mapped[dict]


# sanduiche[ingredients] --> {
#     'hamburguer': 180g
#     'pão': 1u
# }


@mapped_as_dataclass(table_registry)
class Ingredient:
    __tablename__ = 'ingredients'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    quantity: Mapped[float]
    unit_of_measure: Mapped[str]
    minimum: Mapped[float]


@mapped_as_dataclass(table_registry)
class Order:
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    ordered_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    client: Mapped[int]  # Client id
    products: Mapped[list]


# products = [
#     {'sanduiche': 2},
#     {'coca-300': 2}
# ]

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


class UnitOfMeasure(str, Enum):
    litro = 'L'
    quilograma = 'Kg'
    unidade = 'Unidade(s)'


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    phone: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str] = mapped_column(nullable=True)

    orders: Mapped[list['Order']] = relationship(init=False, lazy='select')


@table_registry.mapped_as_dataclass
class Order:
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    ordered_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    client_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    notes: Mapped[str] = mapped_column(nullable=True)

    client: Mapped['User'] = relationship(
        init=False, back_populates='orders', lazy='joined'
    )
    order_items: Mapped[list['OrderItem']] = relationship(
        init=False, back_populates='order', lazy='selectin'
    )


@table_registry.mapped_as_dataclass
class OrderItem:
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int]
    unit_price: Mapped[Decimal]

    order: Mapped['Order'] = relationship(
        init=False, back_populates='order_items', lazy='joined'
    )
    product: Mapped['Product'] = relationship(
        init=False, back_populates='order_items', lazy='joined'
    )


@table_registry.mapped_as_dataclass
class Product:
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    preparation_time: Mapped[int]  # minutes

    order_items: Mapped[list['OrderItem']] = relationship(
        init=False, back_populates='product', lazy='noload'
    )
    product_ingredients: Mapped[list['ProductIngredient']] = relationship(
        init=False, back_populates='product', lazy='selectin'
    )


@table_registry.mapped_as_dataclass
class ProductIngredient:
    __tablename__ = 'product_ingredients'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredients.id'))
    quantity: Mapped[Decimal]

    product: Mapped['Product'] = relationship(
        init=False, back_populates='product_ingredients', lazy='joined'
    )
    ingredient: Mapped['Ingredient'] = relationship(
        init=False, back_populates='product_ingredients', lazy='joined'
    )


@table_registry.mapped_as_dataclass
class Ingredient:
    __tablename__ = 'ingredients'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    unit_of_measure: Mapped[UnitOfMeasure]
    minimum: Mapped[Decimal]
    quantity: Mapped[Decimal]

    product_ingredients: Mapped[list['ProductIngredient']] = relationship(
        init=False, back_populates='ingredient', lazy='noload'
    )

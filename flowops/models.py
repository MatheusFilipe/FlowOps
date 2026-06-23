from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    phone: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]

    orders: Mapped[list['Order']] = relationship()


@table_registry.mapped_as_dataclass
class Order:
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    ordered_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    client_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    notes: Mapped[str] = mapped_column(nullable=True)

    client: Mapped['User'] = relationship(back_populates='orders')
    order_items: Mapped[list['OrderItem']] = relationship(
        back_populates='order'
    )


@table_registry.mapped_as_dataclass
class OrderItem:
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int]
    unit_price: Mapped[Decimal]

    order: Mapped['Order'] = relationship(back_populates='order_items')
    product: Mapped['Product'] = relationship(back_populates='order_items')


@table_registry.mapped_as_dataclass
class Product:
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    preparation_time: Mapped[int]  # minutes

    order_items: Mapped[list['OrderItem']] = relationship(
        back_populates='product'
    )
    product_ingredients: Mapped[list['ProductIngredient']] = relationship(
        back_populates='product'
    )


@table_registry.mapped_as_dataclass
class ProductIngredient:
    __tablename__ = 'product_ingredients'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredients.id'))
    quantity: Mapped[Decimal]

    product: Mapped['Product'] = relationship(
        back_populates='product_ingredients'
    )
    ingredient: Mapped['Ingredient'] = relationship(
        back_populates='product_ingredients'
    )


@table_registry.mapped_as_dataclass
class Ingredient:
    __tablename__ = 'ingredients'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    unit_of_measure: Mapped[str]
    minimum: Mapped[Decimal]

    product_ingredients: Mapped[list['ProductIngredient']] = relationship(
        back_populates='ingredient'
    )

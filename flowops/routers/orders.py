from datetime import timedelta
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from flowops.database import get_session
from flowops.models import (
    Ingredient,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    User,
)
from flowops.schemas import (
    OrderCancel,
    OrderList,
    OrderPublic,
    OrderSchema,
)

router = APIRouter(prefix='/orders', tags=['orders'])

Session = Annotated[AsyncSession, Depends(get_session)]


async def check_and_subtract_from_stock(product, product_qty, session):
    required = {
        p.ingredient_id: p.quantity for p in product.product_ingredients
    }

    stmt = select(Ingredient).where(Ingredient.id.in_(required.keys()))
    result = await session.scalars(stmt)
    ingredients = result.all()

    if len(ingredients) != len(required):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Um ou mais ingredientes não foram encontrados.',
        )

    for ingredient in ingredients:
        required_qty = required[ingredient.id] * product_qty

        if required_qty > ingredient.quantity:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_CONTENT,
                detail=(
                    f'Estoque insuficiente para o ingrediente '
                    f'"{ingredient.name}". Disponível: {ingredient.quantity}. '
                    f'Requerido: {required_qty}.'
                )
            )

        ingredient.quantity -= required_qty


def restock_ingredients(order):
    for order_item in order.order_items:
        product_quantity = order_item.quantity
        for product_ingredient in order_item.product.product_ingredients:
            ingredient_quantity = product_ingredient.quantity
            ingredient = product_ingredient.ingredient

            ingredient.quantity += product_quantity * ingredient_quantity


@router.post('/', status_code=HTTPStatus.OK, response_model=OrderPublic)
async def create_order(session: Session, schema: OrderSchema):
    if not await session.scalar(
        select(User).where(User.id == schema.client_id)
    ):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Cliente não encontrado.',
        )

    order = Order(client_id=schema.client_id)

    session.add(order)
    await session.flush()

    final_amount = 0
    order_preparation_time = 0
    for id, quantity in schema.product_quantity.items():
        product = await session.scalar(select(Product).where(Product.id == id))
        if not product:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Produto não encontrado.',
            )

        await check_and_subtract_from_stock(product, quantity, session)

        order_item = OrderItem(
            order_id=order.id,
            product_id=id,
            quantity=quantity,
            unit_price=product.price,
        )

        final_amount += product.price * quantity
        order_preparation_time = max(
            order_preparation_time, product.preparation_time
        )

        session.add(order_item)

    setattr(order, 'notes', schema.notes)
    setattr(order, 'final_amount', final_amount)

    estimated_ready_at = order.ordered_at + timedelta(
        minutes=order_preparation_time
    )
    setattr(order, 'estimated_ready_at', estimated_ready_at)

    await session.commit()
    await session.refresh(order)

    return order


@router.get(
    '/{client_id}', status_code=HTTPStatus.OK, response_model=OrderList
)
async def list_orders(session: Session, client_id: int):
    if not await session.scalar(select(User).where(User.id == client_id)):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Cliente não encontrado.',
        )

    orders = await session.scalars(
        select(Order).where(Order.client_id == client_id)
    )

    return {'orders': orders}


@router.post('/{order_id}', status_code=HTTPStatus.OK, response_model=dict)
async def cancel_order(session: Session, order_id: int, schema: OrderCancel):
    order = await session.scalar(select(Order).where(Order.id == order_id))

    if not order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Pedido não encontrado.',
        )

    if order.status == OrderStatus.being_prepared:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=(
                'O pedido não pode ser cancelado porque já está em preparação.'
            ),
        )
    elif order.status == OrderStatus.completed:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_CONTENT,
            detail=(
                'O pedido não pode ser cancelado porque já está finalizado.'
            ),
        )
    elif order.status == OrderStatus.canceled:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='O pedido não pode ser cancelado porque já está cancelado.',
        )

    restock_ingredients(order)

    order.status = OrderStatus.canceled
    await session.commit()

    return {'reason': schema.reason}

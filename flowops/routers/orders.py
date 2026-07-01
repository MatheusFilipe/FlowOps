from datetime import timedelta
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from flowops.database import get_session
from flowops.models import Order, OrderItem, Product, User
from flowops.schemas import (
    OrderList,
    OrderPublic,
    OrderSchema,
)

router = APIRouter(prefix='/orders', tags=['orders'])

Session = Annotated[Session, Depends(get_session)]


@router.post('/', status_code=HTTPStatus.OK, response_model=OrderPublic)
def create_order(session: Session, schema: OrderSchema):
    if not session.scalar(select(User).where(User.id == schema.client_id)):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Cliente não encontrado.',
        )

    order = Order(
        client_id=schema.client_id,
        notes=schema.notes,
    )

    session.add(order)
    session.commit()

    final_amount = 0
    order_preparation_time = 0
    for id, quantity in schema.product_quantity.items():
        product = session.scalar(select(Product).where(Product.id == id))
        if not product:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Produto não encontrado.',
            )

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

    setattr(order, 'final_amount', final_amount)

    estimated_ready_at = order.ordered_at + timedelta(
        minutes=order_preparation_time
    )
    setattr(order, 'estimated_ready_at', estimated_ready_at)

    session.commit()
    session.refresh(order)

    return order


@router.get(
    '/{client_id}', status_code=HTTPStatus.OK, response_model=OrderList
)
def list_orders(session: Session, client_id: int):
    if not session.scalar(select(User).where(User.id == client_id)):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Cliente não encontrado.',
        )

    orders = session.scalars(select(Order).where(Order.client_id == client_id))

    return {'orders': orders}


@router.delete('/{order_id}', status_code=HTTPStatus.OK, response_model=dict)
def delete_order(session: Session, order_id: int):
    order = session.scalar(select(Order).where(Order.id == order_id))

    if not order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Pedido não encontrado.',
        )

    session.delete(order)
    session.commit()

    return {'message': 'Pedido cancelado.'}

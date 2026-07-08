from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from flowops.database import get_session
from flowops.models import Ingredient, Product, ProductIngredient
from flowops.schemas import (
    ProductList,
    ProductPublic,
    ProductSchema,
    ProductUpdate,
)

router = APIRouter(prefix='/products', tags=['products'])

Session = Annotated[AsyncSession, Depends(get_session)]


@router.post('/', status_code=HTTPStatus.OK, response_model=ProductPublic)
async def create_product(session: Session, schema: ProductSchema):
    product = await session.scalar(
        select(Product).where(Product.name == schema.name)
    )

    if product:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Produto já cadastrado.',
        )

    product = Product(
        name=schema.name,
        description=schema.description,
        preparation_time=schema.preparation_time,
        price=schema.price,
    )

    session.add(product)
    await session.commit()

    product_ingredients = []
    for id, quantity in schema.ingredients_quantity.items():
        if not await session.scalar(
            select(Ingredient).where(Ingredient.id == id)
        ):
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Ingrediente não encontrado.',
            )

        product_ingredient = ProductIngredient(
            product_id=product.id, ingredient_id=id, quantity=quantity
        )

        product_ingredients.append(product_ingredient)

        session.add(product_ingredient)
        await session.commit()
        await session.refresh(product_ingredient)

    await session.refresh(product)

    return product


@router.get('/', status_code=HTTPStatus.OK, response_model=ProductList)
async def list_products(session: Session):
    products = await session.scalars(select(Product))

    return {'products': products}


@router.patch(
    '/{product_id}',
    status_code=HTTPStatus.OK,
    response_model=ProductPublic,
)
async def update_product(
    session: Session, product_id: int, schema: ProductUpdate
):
    product = await session.scalar(
        select(Product).where(Product.id == product_id)
    )

    if not product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Produto não encontrado.',
        )

    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    session.add(product)
    await session.commit()
    await session.refresh(product)

    return product


@router.delete('/{product_id}', status_code=HTTPStatus.OK, response_model=dict)
async def delete_product(session: Session, product_id: int):
    product = await session.scalar(
        select(Product).where(Product.id == product_id)
    )

    if not product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Produto não encontrado.',
        )

    await session.delete(product)
    await session.commit()

    return {'message': 'Produto deletado.'}

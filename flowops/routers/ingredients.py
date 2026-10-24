from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from flowops.database import get_session
from flowops.models import Ingredient, IngredientStatus
from flowops.schemas import (
    IngredientList,
    IngredientPublic,
    IngredientSchema,
    IngredientUpdate,
)

router = APIRouter(prefix='/ingredients', tags=['ingredients'])

Session = Annotated[AsyncSession, Depends(get_session)]


def check_stock(quantity, minimum):
    if quantity == 0:
        return IngredientStatus.out_of_stock
    elif quantity < minimum:
        return IngredientStatus.low_stock
    else:
        return IngredientStatus.ok


@router.post('/', status_code=HTTPStatus.OK, response_model=IngredientPublic)
async def create_ingredient(session: Session, schema: IngredientSchema):
    ingredient = await session.scalar(
        select(Ingredient).where(Ingredient.name == schema.name)
    )

    if ingredient:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Ingrediente já cadastrado.',
        )

    if schema.quantity < 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_CONTENT,
            detail='A quantidade não pode ser negativa.',
        )
    status = check_stock(schema.quantity, schema.minimum)

    ingredient = Ingredient(
        name=schema.name,
        unit_of_measure=schema.unit_of_measure,
        minimum=schema.minimum,
        quantity=schema.quantity,
        status=status,
    )

    session.add(ingredient)
    await session.commit()
    await session.refresh(ingredient)

    return ingredient


@router.get('/', status_code=HTTPStatus.OK, response_model=IngredientList)
async def list_ingredients(session: Session):
    ingredients = await session.scalars(select(Ingredient))

    return {'ingredients': ingredients}


@router.patch(
    '/{ingredient_id}',
    status_code=HTTPStatus.OK,
    response_model=IngredientPublic,
)
async def update_ingredient(
    session: Session, ingredient_id: int, schema: IngredientUpdate
):
    ingredient = await session.scalar(
        select(Ingredient).where(Ingredient.id == ingredient_id)
    )

    if not ingredient:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Ingrediente não encontrado.',
        )

    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(ingredient, key, value)

    ingredient.status = check_stock(ingredient.quantity, ingredient.minimum)

    session.add(ingredient)
    await session.commit()
    await session.refresh(ingredient)

    return ingredient


@router.delete(
    '/{ingredient_id}', status_code=HTTPStatus.OK, response_model=dict
)
async def delete_ingredient(session: Session, ingredient_id: int):
    ingredient = await session.scalar(
        select(Ingredient).where(Ingredient.id == ingredient_id)
    )

    if not ingredient:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Ingrediente não encontrado.',
        )

    await session.delete(ingredient)
    await session.commit()

    return {'message': 'Ingrediente deletado.'}

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from flowops.database import get_session
from flowops.models import Ingredient
from flowops.schemas import (
    IngredientList,
    IngredientPublic,
    IngredientSchema,
    IngredientUpdate,
)

router = APIRouter(prefix='/ingredients', tags=['ingredients'])

Session = Annotated[Session, Depends(get_session)]


@router.post('/', status_code=HTTPStatus.OK, response_model=IngredientPublic)
def create_ingredient(session: Session, schema: IngredientSchema):
    ingredient = session.scalar(
        select(Ingredient).where(Ingredient.name == schema.name)
    )

    if ingredient:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Ingrediente já cadastrado.',
        )

    ingredient = Ingredient(
        name=schema.name,
        unit_of_measure=schema.unit_of_measure,
        minimum=schema.minimum,
        quantity=schema.quantity,
    )

    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return ingredient


@router.get('/', status_code=HTTPStatus.OK, response_model=IngredientList)
def list_ingredients(session: Session):
    ingredients = session.scalars(select(Ingredient))

    return {'ingredients': ingredients}


@router.patch(
    '/{ingredient_id}',
    status_code=HTTPStatus.OK,
    response_model=IngredientPublic,
)
def update_ingredient(
    session: Session, ingredient_id: int, schema: IngredientUpdate
):
    ingredient = session.scalar(
        select(Ingredient).where(Ingredient.id == ingredient_id)
    )

    if not ingredient:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Ingrediente não encontrado.',
        )

    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(ingredient, key, value)

    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return ingredient


@router.delete(
    '/{ingredient_id}', status_code=HTTPStatus.OK, response_model=dict
)
def delete_ingredient(session: Session, ingredient_id: int):
    ingredient = session.scalar(
        select(Ingredient).where(Ingredient.id == ingredient_id)
    )

    if not ingredient:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Ingrediente não encontrado.',
        )

    session.delete(ingredient)
    session.commit()

    return {'message': 'Ingrediente deletado.'}

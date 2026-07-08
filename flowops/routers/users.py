from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from flowops.database import get_session
from flowops.models import User
from flowops.schemas import (
    UserList,
    UserPublic,
    UserSchema,
    UserUpdate,
)

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[AsyncSession, Depends(get_session)]


@router.post('/', status_code=HTTPStatus.OK, response_model=UserPublic)
async def create_user(session: Session, schema: UserSchema):
    user = await session.scalar(select(User).where(User.phone == schema.phone))

    if user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Usuário já cadastrado.',
        )

    user = User(
        name=schema.name,
        phone=schema.phone,
        address=schema.address,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def list_users(session: Session):
    users = await session.scalars(select(User))

    return {'users': users}


@router.patch(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
async def update_user(session: Session, user_id: int, schema: UserUpdate):
    user = await session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado.',
        )

    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=dict)
async def delete_user(session: Session, user_id: int):
    user = await session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado.',
        )

    await session.delete(user)
    await session.commit()

    return {'message': 'Usuário deletado.'}

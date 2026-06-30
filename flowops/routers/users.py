from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from flowops.database import get_session
from flowops.models import User
from flowops.schemas import (
    UserList,
    UserPublic,
    UserSchema,
    UserUpdate,
)

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[Session, Depends(get_session)]


@router.post('/', status_code=HTTPStatus.OK, response_model=UserPublic)
def create_user(session: Session, schema: UserSchema):
    user = session.scalar(select(User).where(User.phone == schema.phone))

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
    session.commit()
    session.refresh(user)

    return user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def list_users(session: Session):
    users = session.scalars(select(User))

    return {'users': users}


@router.patch(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
def update_user(session: Session, user_id: int, schema: UserUpdate):
    user = session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado.',
        )

    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=dict)
def delete_user(session: Session, user_id: int):
    user = session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado.',
        )

    session.delete(user)
    session.commit()

    return {'message': 'Usuário deletado.'}

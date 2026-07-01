from contextlib import contextmanager
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from flowops.app import app
from flowops.database import get_session
from flowops.models import (
    Ingredient,
    Order,
    OrderItem,
    Product,
    ProductIngredient,
    UnitOfMeasure,
    User,
    table_registry,
)


@contextmanager
def _mock_db_time(
    *, model, time=datetime(2001, 9, 11, 8, 46, 0), order_preparation_time=0
    ):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'ordered_at'):
            target.ordered_at = time
        if hasattr(target, 'estimated_ready_at'):
            target.estimated_ready_at = time + timedelta(
                minutes=order_preparation_time
            )

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def ingredient(session):
    ingredient = Ingredient(
        name='ingredient',
        unit_of_measure=UnitOfMeasure.unidade,
        minimum='10',
        quantity='0',
    )

    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return ingredient


@pytest.fixture
def product(session, ingredient):
    product = Product(
        name='product',
        description='description',
        preparation_time=15,
        price=10,
    )

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


@pytest.fixture
def product_ingredient(session, product, ingredient):
    product_ingredient = ProductIngredient(
        product_id=product.id, ingredient_id=ingredient.id, quantity=5
    )

    session.add(product_ingredient)
    session.commit()
    session.refresh(product_ingredient)

    return product_ingredient


@pytest.fixture
def user(session):
    user = User(
        name='user',
        phone='tel:+55-11-4002-8922',
        address='Rua dos Bobos, n° 0',
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def order(session, user, product, mock_db_time):
    with mock_db_time(
        model=Order, order_preparation_time=product.preparation_time
    ):
        order = Order(
            client_id=user.id,
            notes='notes',
        )
        session.add(order)
        session.commit()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        unit_price=product.price,
    )
    session.add(order_item)

    order.final_amount = order_item.unit_price * order_item.quantity

    session.commit()
    session.refresh(order)

    return order

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from flowops.app import app
from flowops.database import get_session
from flowops.models import Ingredient, UnitOfMeasure, table_registry


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
        name='ingrediente',
        unit_of_measure=UnitOfMeasure.unidade,
        minimum='10',
        quantity='0',
    )

    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return ingredient

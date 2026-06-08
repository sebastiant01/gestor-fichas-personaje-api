from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from src.app.api_config import app
from src.database.base import Base
from src.entities.usuario import Usuario
from src.entities.au import Au
from src.entities.ficha_personaje import FichaPersonaje


@pytest.fixture(scope="function")
def engine():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    from sqlalchemy.dialects import sqlite
    import sqlalchemy.types as types

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db(engine):
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c

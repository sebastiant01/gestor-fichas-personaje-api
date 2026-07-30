"""
Fixtures compartidas de pytest: SQLite en memoria, cliente HTTP y tokens.

Los tests de routers pueden definir fixtures locales adicionales (p. ej. ``usuario_admin``).
"""

from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from api_config import app
from src.database.base import Base
from src.entities.usuario import Usuario
from src.entities.au import Au
from src.entities.ficha_personaje import FichaPersonaje

from src.utils.hash_password import hash_password
from src.utils.jwt_auth import crear_token
from src.repositories import usuario_repository

from src.database.session import get_db


@pytest.fixture(scope="function")
def engine():
    """Motor SQLite en memoria con pool estático para aislar cada test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    from sqlalchemy.dialects import sqlite
    import sqlalchemy.types as types

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db(engine):
    """Sesión SQLAlchemy por test con rollback al finalizar."""
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def token_admin(usuario_admin: Usuario) -> str:
    """JWT de access para un usuario admin (requiere fixture ``usuario_admin``)."""
    return crear_token(
        data={
            "sub": str(usuario_admin.id_usuario),
            "nombre_usuario": usuario_admin.nombre_usuario,
            "es_admin": usuario_admin.es_admin,
        },
        tipo_token="access",
    )


@pytest.fixture
def headers_admin(token_admin: str) -> dict:
    """Cabecera ``Authorization`` lista para peticiones autenticadas."""
    return {"Authorization": f"Bearer {token_admin}"}


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    """``TestClient`` de FastAPI con ``get_db`` sobreescrito a la sesión de test."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

import uuid

"""Tests de integración HTTP del router ``ficha_personaje_router``."""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.utils.hash_password import hash_password
from src.entities.usuario import Usuario
from src.entities.au import Au
from src.entities.ficha_personaje import FichaPersonaje
from src.repositories import (
    usuario_repository,
    au_repository,
    ficha_personaje_repository,
)
from src.utils.jwt_auth import crear_token


@pytest.fixture
def usuario_admin(db: Session) -> Usuario:
    usuario = Usuario(
        nombre_usuario="coche",
        contrasena_hash=hash_password("coche123"),
        es_admin=True,
    )
    return usuario_repository.crear_usuario(db=db, usuario=usuario)


@pytest.fixture
def headers_admin(usuario_admin: Usuario) -> dict:
    token = crear_token(
        data={
            "sub": str(usuario_admin.id_usuario),
            "nombre_usuario": usuario_admin.nombre_usuario,
            "es_admin": usuario_admin.es_admin,
        },
        tipo_token="access",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def au_base(db: Session, usuario_admin: Usuario) -> Au:
    au = Au(id_usuario=usuario_admin.id_usuario, nombre_au="cat")
    return au_repository.crear_au(db=db, au=au)


@pytest.fixture
def au_idols(db: Session, usuario_admin: Usuario) -> Au:
    au = Au(id_usuario=usuario_admin.id_usuario, nombre_au="idols")
    return au_repository.crear_au(db=db, au=au)


@pytest.fixture
def ficha_base(db: Session, usuario_admin: Usuario, au_base: Au) -> FichaPersonaje:
    ficha = FichaPersonaje(
        id_usuario=usuario_admin.id_usuario,
        id_au=au_base.id_au,
        nombre_personaje="Sakura",
        sexo="Femenino",
        fecha_cumpleanos=date(2000, 4, 1),
    )
    return ficha_personaje_repository.crear_ficha_personaje(db=db, ficha=ficha)


def test_obtener_fichas(
    client: TestClient, ficha_base: FichaPersonaje, headers_admin: dict
):
    response = client.get("/fichas/", headers=headers_admin)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_obtener_ficha_por_id(
    client: TestClient, ficha_base: FichaPersonaje, headers_admin: dict
):
    response = client.get(
        f"/fichas/{ficha_base.id_ficha_personaje}", headers=headers_admin
    )
    assert response.status_code == 200
    assert response.json()["nombre_personaje"] == "Sakura"


def test_obtener_fichas_por_nombre(
    client: TestClient, ficha_base: FichaPersonaje, headers_admin: dict
):
    response = client.get(
        "/fichas/buscar/nombre?nombre_personaje=Sakura", headers=headers_admin
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_obtener_fichas_por_signo(
    client: TestClient, ficha_base: FichaPersonaje, headers_admin: dict
):
    response = client.get(
        "/fichas/buscar/signo?signo_zodiacal=Aries", headers=headers_admin
    )
    assert response.status_code == 200


def test_obtener_fichas_por_sexo(
    client: TestClient, ficha_base: FichaPersonaje, headers_admin: dict
):
    response = client.get("/fichas/buscar/sexo?sexo=Femenino", headers=headers_admin)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_obtener_fichas_por_mes(
    client: TestClient, ficha_base: FichaPersonaje, headers_admin: dict
):
    response = client.get("/fichas/buscar/cumpleanos/mes?mes=4", headers=headers_admin)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_obtener_fichas_por_dia(
    client: TestClient, ficha_base: FichaPersonaje, headers_admin: dict
):
    response = client.get("/fichas/buscar/cumpleanos/dia?dia=1", headers=headers_admin)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_crear_ficha(client: TestClient, au_base: Au, headers_admin: dict):
    response = client.post(
        "/fichas/",
        json={
            "id_au": str(au_base.id_au),
            "nombre_personaje": "Hinata",
            "sexo": "Femenino",
            "fecha_cumpleanos": "2001-07-01",
        },
        headers=headers_admin,
    )
    assert response.status_code == 201
    assert response.json()["nombre_personaje"] == "Hinata"


def test_crear_ficha_con_edad_en_idols(
    client: TestClient, au_idols: Au, headers_admin: dict
):
    response = client.post(
        "/fichas/",
        json={
            "id_au": str(au_idols.id_au),
            "nombre_personaje": "Hoshi",
            "sexo": "Masculino",
            "fecha_cumpleanos": "1996-06-15",
            "edad": 28,
        },
        headers=headers_admin,
    )
    assert response.status_code == 201
    assert response.json()["edad"] == 28


def test_crear_ficha_edad_en_au_no_idols(
    client: TestClient, au_base: Au, headers_admin: dict
):
    response = client.post(
        "/fichas/",
        json={
            "id_au": str(au_base.id_au),
            "nombre_personaje": "Sakura",
            "sexo": "Femenino",
            "fecha_cumpleanos": "2000-04-01",
            "edad": 20,
        },
        headers=headers_admin,
    )
    assert response.status_code == 400


def test_actualizar_ficha(
    client: TestClient, ficha_base: FichaPersonaje, headers_admin: dict
):
    response = client.patch(
        f"/fichas/{ficha_base.id_ficha_personaje}",
        json={"nombre_personaje": "Sakura 🌸"},
        headers=headers_admin,
    )
    assert response.status_code == 200
    assert response.json()["nombre_personaje"] == "Sakura 🌸"


def test_eliminar_ficha(
    client: TestClient, ficha_base: FichaPersonaje, headers_admin: dict
):
    response = client.delete(
        f"/fichas/{ficha_base.id_ficha_personaje}", headers=headers_admin
    )
    assert response.status_code == 204


def test_endpoint_sin_token(client: TestClient):
    response = client.get("/fichas/")
    assert response.status_code == 401

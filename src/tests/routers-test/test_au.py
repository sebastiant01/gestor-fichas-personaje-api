import pytest
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
def ficha_base(db: Session, usuario_admin: Usuario, au_base: Au) -> FichaPersonaje:
    from datetime import date

    ficha = FichaPersonaje(
        id_usuario=usuario_admin.id_usuario,
        id_au=au_base.id_au,
        nombre_personaje="Test Personaje",
        sexo="femenino",
        fecha_cumpleanos=date(2000, 1, 1),
    )
    return ficha_personaje_repository.crear_ficha_personaje(db=db, ficha=ficha)


def test_obtener_aus(client: TestClient, au_base: Au, headers_admin: dict):
    response = client.get("/aus/", headers=headers_admin)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_obtener_au_por_id(client: TestClient, au_base: Au, headers_admin: dict):
    response = client.get(f"/aus/{au_base.id_au}", headers=headers_admin)
    assert response.status_code == 200
    assert response.json()["nombre_au"] == "cat"


def test_obtener_fichas_de_au(
    client: TestClient, ficha_base: FichaPersonaje, headers_admin: dict
):
    response = client.get(f"/aus/{ficha_base.id_au}/fichas", headers=headers_admin)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nombre_personaje"] == "Test Personaje"


def test_obtener_fichas_de_au_vacio(
    client: TestClient, au_base: Au, headers_admin: dict
):
    response = client.get(f"/aus/{au_base.id_au}/fichas", headers=headers_admin)
    assert response.status_code == 200
    assert response.json() == []


def test_obtener_au_por_nombre(client: TestClient, au_base: Au, headers_admin: dict):
    response = client.get("/aus/buscar?nombre_au=cat", headers=headers_admin)
    assert response.status_code == 200
    assert response.json()["nombre_au"] == "cat"


def test_obtener_au_inexistente(client: TestClient, headers_admin: dict):
    import uuid

    response = client.get(f"/aus/{uuid.uuid4()}", headers=headers_admin)
    assert response.status_code == 404


def test_crear_au(client: TestClient, headers_admin: dict, usuario_admin: Usuario):
    response = client.post(
        "/aus/",
        json={"nombre_au": "yyxy", "descripcion_au": "AU de yyxy"},
        headers=headers_admin,
    )
    assert response.status_code == 201
    assert response.json()["nombre_au"] == "yyxy"


def test_crear_au_duplicado(client: TestClient, au_base: Au, headers_admin: dict):
    response = client.post(
        "/aus/",
        json={"nombre_au": "cat"},
        headers=headers_admin,
    )
    assert response.status_code == 409


def test_actualizar_au(client: TestClient, au_base: Au, headers_admin: dict):
    response = client.patch(
        f"/aus/{au_base.id_au}",
        json={"nombre_au": "idols"},
        headers=headers_admin,
    )
    assert response.status_code == 200
    assert response.json()["nombre_au"] == "idols"


def test_eliminar_au(client: TestClient, au_base: Au, headers_admin: dict):
    response = client.delete(f"/aus/{au_base.id_au}", headers=headers_admin)
    assert response.status_code == 204


def test_endpoint_sin_token(client: TestClient):
    response = client.get("/aus/")
    assert response.status_code == 401

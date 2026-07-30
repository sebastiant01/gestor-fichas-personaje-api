import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.utils.hash_password import hash_password
from src.entities.usuario import Usuario
from src.repositories import usuario_repository
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


def test_obtener_usuario_actual(
    client: TestClient, usuario_admin: Usuario, headers_admin: dict
):
    response = client.get("/usuarios/me", headers=headers_admin)
    assert response.status_code == 200
    assert response.json()["nombre_usuario"] == "coche"


def test_crear_usuario(client: TestClient, headers_admin: dict, usuario_admin: Usuario):
    response = client.post(
        "/usuarios/",
        json={"nombre_usuario": "nueva", "contrasena": "nueva123"},
        headers=headers_admin,
    )
    assert response.status_code == 201
    assert response.json()["nombre_usuario"] == "nueva"


def test_crear_usuario_duplicado(
    client: TestClient, headers_admin: dict, usuario_admin: Usuario
):
    response = client.post(
        "/usuarios/",
        json={"nombre_usuario": "coche", "contrasena": "coche123"},
        headers=headers_admin,
    )
    assert response.status_code == 409


def test_actualizar_usuario(
    client: TestClient, headers_admin: dict, usuario_admin: Usuario
):
    response = client.patch(
        "/usuarios/me",
        json={"nombre_usuario": "coche_v2"},
        headers=headers_admin,
    )
    assert response.status_code == 200
    assert response.json()["nombre_usuario"] == "coche_v2"


def test_eliminar_usuario(
    client: TestClient, headers_admin: dict, usuario_admin: Usuario
):
    response = client.delete("/usuarios/me", headers=headers_admin)
    assert response.status_code == 204


def test_endpoint_sin_token(client: TestClient):
    response = client.get("/usuarios/")
    assert response.status_code == 401

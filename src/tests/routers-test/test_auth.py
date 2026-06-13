import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.utils.hash_password import hash_password
from src.entities.usuario import Usuario
from src.repositories import usuario_repository


@pytest.fixture
def usuario_admin(db: Session) -> Usuario:
    usuario = Usuario(
        nombre_usuario="coche",
        contrasena_hash=hash_password("coche123"),
        es_admin=True,
    )
    return usuario_repository.crear_usuario(db=db, usuario=usuario)


def test_login_exitoso(client: TestClient, usuario_admin: Usuario):
    response = client.post(
        "/auth/login",
        data={"username": "coche", "password": "coche123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_contrasena_incorrecta(client: TestClient, usuario_admin: Usuario):
    response = client.post(
        "/auth/login",
        data={"username": "coche", "password": "incorrecta"},
    )
    assert response.status_code == 401


def test_login_usuario_inexistente(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "fantasma", "password": "coche123"},
    )
    assert response.status_code == 404


def test_login_usuario_no_admin(client: TestClient, db: Session):
    usuario = Usuario(
        nombre_usuario="invitado",
        contrasena_hash=hash_password("invitado123"),
        es_admin=False,
    )
    usuario_repository.crear_usuario(db=db, usuario=usuario)

    response = client.post(
        "/auth/login",
        data={"username": "invitado", "password": "invitado123"},
    )
    assert response.status_code == 401


def test_refresh_token_exitoso(client: TestClient, usuario_admin: Usuario):
    login = client.post(
        "/auth/login",
        data={"username": "coche", "password": "coche123"},
    )
    refresh_token = login.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_invalido(client: TestClient):
    response = client.post("/auth/refresh", json={"refresh_token": "token_invalido"})
    assert response.status_code == 401

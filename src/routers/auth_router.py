"""Endpoints de autenticación: login OAuth2 y renovación de tokens."""

from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.entities.usuario import Usuario
from src.schemas.auth_schema import TokenResponse, RefreshTokenResponse
from src.services import usuario_service
from src.database.session import get_db
from src.exceptions.excepciones import ErrorNoAutorizadoJWT
from src.utils.hash_password import verify_password
from src.utils.jwt_auth import (
    crear_token,
    renovar_token,
    _extraer_data_payload,
)

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(path="/login", response_model=TokenResponse)
def login_usuario(
    credenciales: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    """Autentica a un usuario administrador y emite un par de tokens JWT.

    Verifica el nombre de usuario y la contraseña recibidos mediante el
    formulario OAuth2, confirma que el usuario tenga privilegios de
    administrador y, de ser así, genera un access token y un refresh token.

    Args:
        credenciales: Formulario OAuth2 con ``username`` y ``password``.
        db: Sesión de base de datos inyectada por dependencia.

    Returns:
        TokenResponse: Par de tokens access y refresh recién generados.

    Raises:
        ErrorNoAutorizadoJWT: Si la contraseña es incorrecta o el usuario
            no tiene permisos de administrador.
    """
    usuario: Usuario = usuario_service.obtener_usuario_por_nombre_usuario(
        db=db, nombre_usuario=credenciales.username
    )
    if not verify_password(
        hashed_password=usuario.contrasena_hash, password=credenciales.password
    ):
        raise ErrorNoAutorizadoJWT(
            mensaje="Error: El usuario o contraseña son incorrectos."
        )
    if not usuario.es_admin:
        raise ErrorNoAutorizadoJWT(mensaje="No tienes permiso para acceder.")

    data = {
        "sub": str(usuario.id_usuario),
        "nombre_usuario": usuario.nombre_usuario,
        "es_admin": usuario.es_admin,
    }

    return TokenResponse(
        access_token=crear_token(data=data, tipo_token="access"),
        refresh_token=crear_token(data=data, tipo_token="refresh"),
    )


@auth_router.post(path="/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshTokenResponse):
    """Renueva un par de tokens JWT a partir de un refresh token válido.

    Args:
        body: Cuerpo de la petición con el ``refresh_token`` a renovar.

    Returns:
        TokenResponse: Nuevo access token y nuevo refresh token.

    Raises:
        ErrorNoAutorizadoJWT: Si el refresh token es inválido o expiró.
    """
    nuevo_access_token = renovar_token(token=body.refresh_token)
    nuevo_refresh_token = crear_token(
        data=_extraer_data_payload(body.refresh_token), tipo_token="refresh"
    )
    return TokenResponse(
        access_token=nuevo_access_token,
        refresh_token=nuevo_refresh_token,
    )

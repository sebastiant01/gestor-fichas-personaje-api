from datetime import timedelta

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.entities.usuario import Usuario
from src.schemas.auth_schema import TokenResponse, RefreshTokenResponse
from src.services import usuario_service
from src.database.session import get_db
from src.exceptions.excepciones import ErrorDatosInvalidos, ErrorNoAutorizadoJWT
from src.utils.hash_password import verify_password
from src.utils.jwt_auth import (
    crear_token,
    renovar_token,
    _decodificar_token,
    _extraer_data_payload,
)

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(path="/login", response_model=TokenResponse)
def login_usuario(
    credenciales: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
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
def refresh_token(body: RefreshTokenResponse, db: Session = Depends(get_db)):
    nuevo_access_token = renovar_token(token=body.refresh_token)
    nuevo_refresh_token = crear_token(
        data=_extraer_data_payload(body.refresh_token), tipo_token="refresh"
    )
    return TokenResponse(
        access_token=nuevo_access_token,
        refresh_token=nuevo_refresh_token,
    )

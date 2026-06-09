from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from uuid import UUID

from src.entities.usuario import Usuario
from src.schemas.auth_schema import UsuarioLogin, TokenResponse
from src.repositories import usuario_repository
from src.database.session import get_db
from src.exceptions.excepciones import ErrorDatosInvalidos
from src.utils.hash_password import verify_password
from src.utils.jwt_auth import crear_token

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(path="/login", response_model=TokenResponse)
def login_usuario(credenciales: UsuarioLogin, db: Session = Depends(get_db)):
    usuario: Usuario | None = usuario_repository.obtener_usuario_por_nombre_usuario(
        db=db, nombre_usuario=credenciales.nombre_usuario
    )
    if not usuario:
        raise ErrorDatosInvalidos(
            mensaje="Error: El usuario o contraseña son incorrectos."
        )
    if not verify_password(
        hashed_password=usuario.contrasena_hash, password=credenciales.contrasena
    ):
        raise ErrorDatosInvalidos(
            mensaje="Error: El usuario o contraseña son incorrectos."
        )

    token: str = crear_token(
        data={
            "sub": str(usuario.id_usuario),
            "nombre_usuario": usuario.nombre_usuario,
            "es_admin": usuario.es_admin,
        }
    )
    return TokenResponse(access_token=token)

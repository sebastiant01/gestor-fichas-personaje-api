from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.entities.usuario import Usuario
from src.schemas.auth_schema import TokenResponse
from src.services import usuario_service
from src.database.session import get_db
from src.exceptions.excepciones import ErrorDatosInvalidos, ErrorNoAutorizadoJWT
from src.utils.hash_password import verify_password
from src.utils.jwt_auth import crear_token

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
        raise ErrorDatosInvalidos(
            mensaje="Error: El usuario o contraseña son incorrectos."
        )
    if not usuario.es_admin:
        raise ErrorNoAutorizadoJWT(mensaje="No tienes permiso para acceder.")

    token: str = crear_token(
        data={
            "sub": str(usuario.id_usuario),
            "nombre_usuario": usuario.nombre_usuario,
            "es_admin": usuario.es_admin,
        }
    )
    return TokenResponse(access_token=token)

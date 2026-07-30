"""Endpoints CRUD del perfil de usuario autenticado (admin)."""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from typing import Any, Annotated

from src.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from src.database.session import get_db
from src.services import usuario_service
from src.utils.jwt_auth import verificar_admin, get_id_usuario

usuario_router: APIRouter = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@usuario_router.get(
    path="/me", status_code=status.HTTP_200_OK, response_model=UsuarioResponse
)
def obtener_usuario_actual(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    """Devuelve los datos del usuario asociado al JWT recibido.

    Args:
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        UsuarioResponse: Datos del usuario autenticado.

    Raises:
        ErrorNoEncontrado: Si el usuario del token ya no existe.
    """
    return usuario_service.obtener_usuario_por_id(
        db=db, id_usuario=get_id_usuario(payload=payload)
    )


@usuario_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=UsuarioResponse,
    dependencies=[Depends(verificar_admin)],
)
def crear_usuario(
    datos: UsuarioCreate,
    db: Annotated[Session, Depends(get_db)],
):
    """Registra un nuevo usuario (requiere un administrador autenticado).

    Args:
        datos: Nombre de usuario y contraseña del nuevo usuario.
        db: Sesión de base de datos inyectada por dependencia.

    Returns:
        UsuarioResponse: Usuario recién creado.

    Raises:
        ErrorDatosInvalidos: Si el nombre o la contraseña son inválidos.
        AppException: Si ya existe un usuario con ese nombre (409).
    """
    return usuario_service.crear_usuario(
        db=db,
        nombre_usuario=datos.nombre_usuario,
        contrasena=datos.contrasena,
    )


@usuario_router.patch(
    path="/me", status_code=status.HTTP_200_OK, response_model=UsuarioResponse
)
def actualizar_usuario(
    datos: UsuarioUpdate,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    """Actualiza el perfil del usuario asociado al JWT recibido.

    Args:
        datos: Campos a modificar; los valores ``None`` se ignoran.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        UsuarioResponse: Usuario actualizado.

    Raises:
        ErrorNoEncontrado: Si el usuario del token ya no existe.
        ErrorDatosInvalidos: Si no se envía ningún dato para actualizar.
    """
    return usuario_service.actualizar_usuario(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        **datos.model_dump(exclude_none=True),
    )


@usuario_router.delete(path="/me", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    """Elimina la cuenta del usuario asociado al JWT recibido.

    Args:
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Raises:
        ErrorNoEncontrado: Si el usuario del token ya no existe.
    """
    usuario_service.eliminar_usuario(db=db, id_usuario=get_id_usuario(payload=payload))

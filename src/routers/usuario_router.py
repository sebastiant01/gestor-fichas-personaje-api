from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Query
from typing import Any, List, Annotated
from uuid import UUID

from src.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from src.database.session import get_db
from src.services import usuario_service
from src.utils.jwt_auth import verificar_admin, get_id_usuario

usuario_router: APIRouter = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@usuario_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=List[UsuarioResponse],
    deprecated=True,
)
def obtener_usuarios(
    skip: Annotated[int, Query(0, ge=0)],
    limit: Annotated[int, Query(100, ge=1, le=100)],
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return usuario_service.obtener_usuarios(db=db, skip=skip, limit=limit)


@usuario_router.get(
    path="/me", status_code=status.HTTP_200_OK, response_model=UsuarioResponse
)
def obtener_usuario_actual(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return usuario_service.obtener_usuario_por_id(
        db=db, id_usuario=get_id_usuario(payload=payload)
    )


@usuario_router.get(
    path="/buscar",
    status_code=status.HTTP_200_OK,
    response_model=UsuarioResponse,
    deprecated=True,
)
def obtener_usuario_por_nombre(
    nombre_usuario: str = Query(..., min_length=1, max_length=40),
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    return usuario_service.obtener_usuario_por_nombre_usuario(
        db=db, nombre_usuario=nombre_usuario
    )


@usuario_router.get(
    path="/{id_usuario}",
    status_code=status.HTTP_200_OK,
    response_model=UsuarioResponse,
    deprecated=True,
)
def obtener_usuario_por_id(
    id_usuario: UUID,
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    return usuario_service.obtener_usuario_por_id(db=db, id_usuario=id_usuario)


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
    usuario_service.eliminar_usuario(db=db, id_usuario=get_id_usuario(payload=payload))

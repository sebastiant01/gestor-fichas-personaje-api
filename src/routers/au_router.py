from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, status
from typing import Any, List, Annotated
from uuid import UUID

from src.schemas.au_schema import AuCreate, AuUpdate, AuResponse
from src.schemas.ficha_personaje_schema import FichaPersonajeResponse
from src.database.session import get_db
from src.services import au_service
from src.services import ficha_personaje_service
from src.utils.jwt_auth import verificar_admin, get_id_usuario

au_router: APIRouter = APIRouter(prefix="/aus", tags=["AUs"])


@au_router.get(
    path="/", status_code=status.HTTP_200_OK, response_model=List[AuResponse]
)
def obtener_aus_por_id_usuario(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return au_service.obtener_aus_por_usuario(
        db=db, id_usuario=get_id_usuario(payload=payload), skip=skip, limit=limit
    )


@au_router.get(
    path="/buscar", status_code=status.HTTP_200_OK, response_model=AuResponse
)
def obtener_au_por_nombre(
    nombre_au: str,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return au_service.obtener_au_por_nombre(
        db=db, id_usuario=get_id_usuario(payload=payload), nombre_au=nombre_au
    )


@au_router.get(
    path="/{id_au}", status_code=status.HTTP_200_OK, response_model=AuResponse
)
def obtener_au_por_id(
    id_au: UUID,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return au_service.obtener_au_por_id(
        db=db, id_au=id_au, id_usuario=get_id_usuario(payload=payload)
    )


@au_router.get(
    path="/{id_au}/fichas",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_de_au(
    id_au: UUID,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return ficha_personaje_service.obtener_fichas_por_au(
        db=db, id_usuario=get_id_usuario(payload=payload), id_au=id_au
    )


@au_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=AuResponse
)
def crear_au(
    datos: AuCreate,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return au_service.crear_au(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        nombre_au=datos.nombre_au,
        descripcion_au=datos.descripcion_au,
    )


@au_router.patch(
    path="/{id_au}", status_code=status.HTTP_200_OK, response_model=AuResponse
)
def actualizar_au(
    id_au: UUID,
    datos: AuUpdate,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return au_service.actualizar_au(
        db=db,
        id_au=id_au,
        id_usuario=get_id_usuario(payload=payload),
        **datos.model_dump(exclude_none=True),
    )


@au_router.delete(path="/{id_au}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_au(
    id_au: UUID,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    au_service.eliminar_au(
        db=db, id_au=id_au, id_usuario=get_id_usuario(payload=payload)
    )

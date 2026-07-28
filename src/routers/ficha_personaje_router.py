from datetime import date
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Query, UploadFile
from pydantic import BaseModel, Field
from typing import Any, List, Annotated
from uuid import UUID

from src.schemas.ficha_personaje_schema import (
    FichaPersonajeCreate,
    FichaPersonajeUpdate,
    FichaPersonajeResponse,
)
from src.database.session import get_db
from src.services import ficha_personaje_service
from src.utils.jwt_auth import verificar_admin, get_id_usuario

ficha_router: APIRouter = APIRouter(prefix="/fichas", tags=["Fichas de personaje"])


class FiltroRequest(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=100)


@ficha_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_usuario(
    filtros: Annotated[FiltroRequest, Query()],
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return ficha_personaje_service.obtener_fichas_por_usuario(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        skip=filtros.skip,
        limit=filtros.limit,
    )


@ficha_router.get(
    path="/buscar/nombre",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_nombre(
    filtros: Annotated[FiltroRequest, Query()],
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
    nombre_personaje: Annotated[str, Query(..., min_length=1, max_length=100)],
):
    return ficha_personaje_service.obtener_fichas_por_nombre_personaje(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        nombre_personaje=nombre_personaje,
        skip=filtros.skip,
        limit=filtros.limit,
    )


@ficha_router.get(
    path="/buscar/signo",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_signo(
    filtros: Annotated[FiltroRequest, Query()],
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
    signo_zodiacal: Annotated[str, Query(..., min_length=1, max_length=20)],
):
    return ficha_personaje_service.obtener_fichas_por_signo(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        signo_zodiacal=signo_zodiacal,
        skip=filtros.skip,
        limit=filtros.limit,
    )


@ficha_router.get(
    path="/buscar/sexo",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_sexo(
    sexo: Annotated[str, Query(..., min_length=1, max_length=30)],
    filtros: Annotated[FiltroRequest, Query()],
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return ficha_personaje_service.obtener_fichas_por_sexo(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        sexo=sexo,
        skip=filtros.skip,
        limit=filtros.limit,
    )


@ficha_router.get(
    path="/buscar/cumpleanos",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_cumpleanos(
    fecha_cumpleanos: Annotated[date, Query(...)],
    filtros: Annotated[FiltroRequest, Query()],
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return ficha_personaje_service.obtener_fichas_por_cumpleanos(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        fecha_cumpleanos=fecha_cumpleanos,
        skip=filtros.skip,
        limit=filtros.limit,
    )


@ficha_router.get(
    path="/buscar/cumpleanos/dia",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_dia_cumpleanos(
    dia: Annotated[int, Query(..., ge=1, le=31)],
    filtros: Annotated[FiltroRequest, Query()],
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return ficha_personaje_service.obtener_fichas_por_dia_cumpleanos(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        dia=dia,
        skip=filtros.skip,
        limit=filtros.limit,
    )


@ficha_router.get(
    path="/buscar/cumpleanos/mes",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_mes_cumpleanos(
    mes: Annotated[int, Query(..., ge=1, le=31)],
    filtros: Annotated[FiltroRequest, Query()],
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return ficha_personaje_service.obtener_fichas_por_mes_cumpleanos(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        mes=mes,
        skip=filtros.skip,
        limit=filtros.limit,
    )


@ficha_router.get(
    path="/{id_ficha}",
    status_code=status.HTTP_200_OK,
    response_model=FichaPersonajeResponse,
)
def obtener_ficha_por_id(
    id_ficha: UUID,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return ficha_personaje_service.obtener_ficha_por_id(
        db=db,
        id_ficha=id_ficha,
        id_usuario=get_id_usuario(payload=payload),
    )


@ficha_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=FichaPersonajeResponse
)
def crear_ficha(
    datos: FichaPersonajeCreate,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return ficha_personaje_service.crear_ficha_personaje(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        **datos.model_dump(exclude_none=True),
    )


@ficha_router.post(path="/upload-image", status_code=status.HTTP_200_OK)
def subir_imagen_a_ficha(
    imagen: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
    id_ficha: Annotated[UUID | None, Query()] = None,
):
    id_usuario = get_id_usuario(payload=payload)
    url = ficha_personaje_service.subir_imagen_ficha(
        db=db, id_usuario=id_usuario, imagen=imagen, id_ficha=id_ficha
    )
    return {"secure_url": url}


@ficha_router.post(
    path="/remove-image",
    status_code=status.HTTP_200_OK,
    response_model=FichaPersonajeResponse,
)
def remover_imagen_a_ficha(
    id_ficha: UUID,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    id_usuario = get_id_usuario(payload=payload)
    return ficha_personaje_service.remover_imagen(
        db=db, id_ficha=id_ficha, id_usuario=id_usuario
    )


@ficha_router.patch(
    path="/{id_ficha}",
    status_code=status.HTTP_200_OK,
    response_model=FichaPersonajeResponse,
)
def actualizar_ficha(
    id_ficha: UUID,
    datos: FichaPersonajeUpdate,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    return ficha_personaje_service.actualizar_ficha(
        db=db,
        id_ficha=id_ficha,
        id_usuario=get_id_usuario(payload=payload),
        **datos.model_dump(exclude_none=True),
    )


@ficha_router.delete(path="/{id_ficha}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ficha(
    id_ficha: UUID,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    ficha_personaje_service.eliminar_ficha(
        db=db,
        id_ficha=id_ficha,
        id_usuario=get_id_usuario(payload=payload),
    )

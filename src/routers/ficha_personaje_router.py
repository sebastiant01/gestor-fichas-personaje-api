from datetime import date
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Query, UploadFile, HTTPException
from typing import Any, List
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


@ficha_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_usuario(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    return ficha_personaje_service.obtener_fichas_por_usuario(
        db=db, id_usuario=get_id_usuario(payload=payload), skip=skip, limit=limit
    )


@ficha_router.get(
    path="/buscar/nombre",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_nombre(
    nombre_personaje: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    return ficha_personaje_service.obtener_fichas_por_nombre_personaje(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        nombre_personaje=nombre_personaje,
        skip=skip,
        limit=limit,
    )


@ficha_router.get(
    path="/buscar/signo",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_signo(
    signo_zodiacal: str = Query(..., min_length=1, max_length=20),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    return ficha_personaje_service.obtener_fichas_por_signo(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        signo_zodiacal=signo_zodiacal,
        skip=skip,
        limit=limit,
    )


@ficha_router.get(
    path="/buscar/sexo",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_sexo(
    sexo: str = Query(..., min_length=1, max_length=30),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    return ficha_personaje_service.obtener_fichas_por_sexo(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        sexo=sexo,
        skip=skip,
        limit=limit,
    )


@ficha_router.get(
    path="/buscar/cumpleanos",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_cumpleanos(
    fecha_cumpleanos: date = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    return ficha_personaje_service.obtener_fichas_por_cumpleanos(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        fecha_cumpleanos=fecha_cumpleanos,
        skip=skip,
        limit=limit,
    )


@ficha_router.get(
    path="/buscar/cumpleanos/dia",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_dia_cumpleanos(
    dia: int = Query(..., ge=1, le=31),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    return ficha_personaje_service.obtener_fichas_por_dia_cumpleanos(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        dia=dia,
        skip=skip,
        limit=limit,
    )


@ficha_router.get(
    path="/buscar/cumpleanos/mes",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_por_mes_cumpleanos(
    mes: int = Query(..., ge=1, le=12),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    return ficha_personaje_service.obtener_fichas_por_mes_cumpleanos(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        mes=mes,
        skip=skip,
        limit=limit,
    )


@ficha_router.get(
    path="/{id_ficha}",
    status_code=status.HTTP_200_OK,
    response_model=FichaPersonajeResponse,
)
def obtener_ficha_por_id(
    id_ficha: UUID,
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
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
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    return ficha_personaje_service.crear_ficha_personaje(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        **datos.model_dump(exclude_none=True),
    )


@ficha_router.post(path="/upload-image", status_code=status.HTTP_200_OK)
def subir_imagen_a_ficha(
    imagen: UploadFile,
    id_ficha: UUID | None = Query(None),
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
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
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
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
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
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
    db: Session = Depends(get_db),
    payload: dict[str, Any] = Depends(verificar_admin),
):
    ficha_personaje_service.eliminar_ficha(
        db=db,
        id_ficha=id_ficha,
        id_usuario=get_id_usuario(payload=payload),
    )

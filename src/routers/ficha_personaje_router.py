"""Endpoints REST para fichas de personaje, búsquedas e imágenes."""

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
    """Parámetros de paginación reutilizados en rutas de búsqueda.

    Attributes:
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver (1-100).
    """

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
    """Lista todas las fichas de personaje del usuario autenticado.

    Args:
        filtros: Parámetros de paginación (``skip`` y ``limit``).
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        list[FichaPersonajeResponse]: Fichas del usuario.
    """
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
    """Busca fichas de personaje cuyo nombre coincida con el indicado.

    Args:
        filtros: Parámetros de paginación.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.
        nombre_personaje: Nombre de personaje a buscar.

    Returns:
        list[FichaPersonajeResponse]: Fichas que coinciden con el nombre.

    Raises:
        ErrorDatosInvalidos: Si ``nombre_personaje`` está vacío.
    """
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
    """Busca fichas de personaje por signo zodiacal.

    Args:
        filtros: Parámetros de paginación.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.
        signo_zodiacal: Signo zodiacal a buscar.

    Returns:
        list[FichaPersonajeResponse]: Fichas que coinciden con el signo.

    Raises:
        ErrorDatosInvalidos: Si ``signo_zodiacal`` está vacío.
    """
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
    """Busca fichas de personaje por sexo.

    Args:
        sexo: Valor de sexo a buscar.
        filtros: Parámetros de paginación.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        list[FichaPersonajeResponse]: Fichas que coinciden con el sexo.

    Raises:
        ErrorDatosInvalidos: Si ``sexo`` está vacío.
    """
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
    """Busca fichas cuya fecha de cumpleaños coincida exactamente.

    Args:
        fecha_cumpleanos: Fecha exacta de cumpleaños a buscar.
        filtros: Parámetros de paginación.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        list[FichaPersonajeResponse]: Fichas con esa fecha de cumpleaños.
    """
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
    """Busca fichas cuyo cumpleaños cae en un día del mes específico.

    Args:
        dia: Día del mes (1-31) a buscar.
        filtros: Parámetros de paginación.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        list[FichaPersonajeResponse]: Fichas cuyo cumpleaños cae en ese
        día.

    Raises:
        ErrorDatosInvalidos: Si ``dia`` está fuera del rango 1-31.
    """
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
    mes: Annotated[int, Query(..., ge=1, le=12)],
    filtros: Annotated[FiltroRequest, Query()],
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    """Busca fichas cuyo cumpleaños cae en un mes específico.

    Args:
        mes: Mes (1-12) a buscar.
        filtros: Parámetros de paginación.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        list[FichaPersonajeResponse]: Fichas cuyo cumpleaños cae en ese
        mes.

    Raises:
        ErrorDatosInvalidos: Si ``mes`` está fuera del rango 1-12.
    """
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
    """Obtiene una ficha de personaje por su UUID.

    Args:
        id_ficha: Identificador UUID de la ficha.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        FichaPersonajeResponse: Ficha solicitada.

    Raises:
        ErrorNoEncontrado: Si la ficha no existe.
        AppException: Si la ficha no pertenece al usuario autenticado
            (403).
    """
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
    """Crea una ficha de personaje dentro de un AU del usuario autenticado.

    Args:
        datos: Datos de la nueva ficha.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        FichaPersonajeResponse: Ficha recién creada.

    Raises:
        ErrorDatosInvalidos: Si faltan campos obligatorios o la edad no
            es válida para el AU indicado.
        ErrorNoEncontrado: Si el AU indicado no existe.
        AppException: Si el AU no pertenece al usuario autenticado (403).
    """
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
    """Sube una imagen a Cloudinary y, opcionalmente, la asocia a una ficha.

    Args:
        imagen: Archivo de imagen recibido en el cuerpo de la petición.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.
        id_ficha: Identificador de la ficha a la que asociar la imagen,
            usado como ``public_id`` en Cloudinary. Si es ``None``, la
            imagen se sube sin asociarla a ninguna ficha.

    Returns:
        dict: Diccionario con la clave ``secure_url`` de la imagen
        subida.

    Raises:
        ErrorDatosInvalidos: Si el tipo de imagen no está permitido.
        ErrorNoEncontrado: Si ``id_ficha`` no corresponde a ninguna
            ficha.
        AppException: Si la ficha no pertenece al usuario autenticado
            (403).
    """
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
    """Elimina la imagen asociada a una ficha, en base de datos y Cloudinary.

    Args:
        id_ficha: Identificador UUID de la ficha.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        FichaPersonajeResponse: Ficha actualizada sin imagen.

    Raises:
        ErrorNoEncontrado: Si la ficha no existe.
        AppException: Si la ficha no pertenece al usuario autenticado
            (403).
    """
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
    """Actualiza los campos de una ficha de personaje existente.

    Args:
        id_ficha: Identificador UUID de la ficha a actualizar.
        datos: Campos a modificar; los valores ``None`` se ignoran.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        FichaPersonajeResponse: Ficha actualizada.

    Raises:
        ErrorNoEncontrado: Si la ficha o el AU destino no existen.
        AppException: Si la ficha o el AU destino no pertenecen al
            usuario (403).
        ErrorDatosInvalidos: Si no se envían datos, o la edad no es
            válida para el AU destino.
    """
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
    """Elimina una ficha de personaje del usuario autenticado.

    Args:
        id_ficha: Identificador UUID de la ficha a eliminar.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Raises:
        ErrorNoEncontrado: Si la ficha no existe.
        AppException: Si la ficha no pertenece al usuario autenticado
            (403).
    """
    ficha_personaje_service.eliminar_ficha(
        db=db,
        id_ficha=id_ficha,
        id_usuario=get_id_usuario(payload=payload),
    )

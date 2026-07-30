"""Reglas de negocio para universos alternos (AUs).

Incluye control de propiedad, nombres únicos por usuario e invalidación
de cache Redis.
"""

import uuid
import json

from sqlalchemy.orm import Session
from src.entities.au import Au
from src.schemas.au_schema import AuResponse
from src.exceptions.excepciones import (
    AppException,
    ErrorDatosInvalidos,
    ErrorNoEncontrado,
)
from src.repositories import au_repository
from src.utils.caching_redis import (
    obtener_respuesta_cache,
    guardar_respuesta_cache,
    invalidar_cache,
)
from fastapi import status


def _cache_key_aus(id_usuario: uuid.UUID) -> str:
    """Construye la clave Redis para el listado de AUs de un usuario.

    Args:
        id_usuario: Identificador UUID del usuario propietario.

    Returns:
        str: Clave Redis en el formato ``aus:usuario:<id_usuario>``.
    """
    return f"aus:usuario:{id_usuario}"


def crear_au(
    db: Session,
    id_usuario: uuid.UUID,
    nombre_au: str,
    descripcion_au: str | None = None,
) -> Au:
    """Crea un AU para el usuario indicado e invalida su cache de listado.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        nombre_au: Nombre del nuevo AU; debe ser único por usuario.
        descripcion_au: Descripción opcional del AU.

    Returns:
        Au: AU recién creado.

    Raises:
        ErrorDatosInvalidos: Si ``nombre_au`` está vacío.
        AppException: Si ya existe un AU con ese nombre para el usuario
            (409).
    """
    if not nombre_au:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar un nombre para el AU.")

    au_existente: Au | None = au_repository.obtener_au_por_nombre(
        db=db, id_usuario=id_usuario, nombre_au=nombre_au
    )
    if au_existente:
        raise AppException(
            mensaje=f"Error: Ya existe un AU con el nombre '{nombre_au}'.",
            codigo_http=status.HTTP_409_CONFLICT,
        )

    nuevo_au: Au = Au(
        id_usuario=id_usuario,
        nombre_au=nombre_au,
        descripcion_au=descripcion_au,
    )
    au_creado = au_repository.crear_au(db=db, au=nuevo_au)
    cache_key = _cache_key_aus(id_usuario=id_usuario)
    invalidar_cache(cache_key)
    return au_creado


def obtener_aus_por_usuario(
    db: Session, id_usuario: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Au] | list[dict]:
    """Lista los AUs de un usuario, sirviendo desde cache cuando es posible.

    Si existe una respuesta cacheada para la combinación de usuario,
    ``skip`` y ``limit``, se devuelve tal cual; en caso contrario se
    consulta la base de datos y se guarda el resultado en cache.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        list[Au] | list[dict]: Entidades ``Au`` si la consulta fue a
        base de datos, o una lista de diccionarios si el resultado vino
        de cache.
    """
    cache_key = _cache_key_aus(id_usuario=id_usuario)
    resultado_cache = obtener_respuesta_cache(cache_key=cache_key)
    if resultado_cache:
        return resultado_cache

    aus = au_repository.obtener_aus_por_id_usuario(
        db=db, id_usuario=id_usuario, skip=skip, limit=limit
    )
    aus_json = json.dumps(
        [AuResponse.model_validate(au).model_dump(mode="json") for au in aus]
    )
    guardar_respuesta_cache(cache_key=cache_key, valor=aus_json)
    return aus


def obtener_au_por_nombre(
    db: Session, id_usuario: uuid.UUID, nombre_au: str
) -> Au | None:
    """Obtiene un AU por nombre dentro de los AUs del usuario indicado.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        nombre_au: Nombre exacto del AU a buscar.

    Returns:
        Au: AU encontrado.

    Raises:
        ErrorDatosInvalidos: Si ``nombre_au`` está vacío.
        ErrorNoEncontrado: Si no existe un AU con ese nombre.
    """
    if not nombre_au:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar el nombre del AU.")
    au: Au | None = au_repository.obtener_au_por_nombre(
        db=db, id_usuario=id_usuario, nombre_au=nombre_au
    )
    if not au:
        raise ErrorNoEncontrado("AU")
    return au


def obtener_au_por_id(db: Session, id_au: uuid.UUID, id_usuario: uuid.UUID) -> Au:
    """Obtiene un AU verificando que pertenezca al usuario indicado.

    Args:
        db: Sesión de base de datos.
        id_au: Identificador UUID del AU.
        id_usuario: Identificador UUID del usuario propietario esperado.

    Returns:
        Au: AU solicitado.

    Raises:
        ErrorNoEncontrado: Si el AU no existe.
        AppException: Si el AU pertenece a otro usuario (403).
    """
    au: Au | None = au_repository.obtener_au_por_id(db=db, id_au=id_au)
    if not au:
        raise ErrorNoEncontrado("AU")
    if au.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para acceder a este AU.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )
    return au


def actualizar_au(db: Session, id_au: uuid.UUID, id_usuario: uuid.UUID, **kwargs) -> Au:
    """Actualiza un AU propio, validando colisión de nombre e invalidando cache.

    Args:
        db: Sesión de base de datos.
        id_au: Identificador UUID del AU a actualizar.
        id_usuario: Identificador UUID del usuario propietario esperado.
        **kwargs: Campos a actualizar (por ejemplo ``nombre_au`` o
            ``descripcion_au``); los valores ``None`` se ignoran.

    Returns:
        Au: AU actualizado.

    Raises:
        ErrorNoEncontrado: Si el AU no existe.
        AppException: Si el AU pertenece a otro usuario (403), o si el
            nuevo nombre colisiona con otro AU del mismo usuario (409).
        ErrorDatosInvalidos: Si no se envía ningún dato para actualizar.
    """
    au: Au | None = au_repository.obtener_au_por_id(db=db, id_au=id_au)
    if not au:
        raise ErrorNoEncontrado("AU")
    if au.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para modificar este AU.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )

    if "nombre_au" in kwargs and kwargs["nombre_au"] is not None:
        au_existente: Au | None = au_repository.obtener_au_por_nombre(
            db=db, id_usuario=id_usuario, nombre_au=kwargs["nombre_au"]
        )
        if au_existente and au_existente.id_au != id_au:
            raise AppException(
                mensaje=f"Error: Ya existe un AU con el nombre '{kwargs['nombre_au']}'.",
                codigo_http=status.HTTP_409_CONFLICT,
            )

    datos = {key: value for key, value in kwargs.items() if value is not None}
    if not datos:
        raise ErrorDatosInvalidos(
            mensaje="Error: No se enviaron datos para actualizar."
        )
    au_actualizado = au_repository.actualizar_au(db=db, au=au, datos=datos)
    cache_key = _cache_key_aus(id_usuario=id_usuario)
    invalidar_cache(cache_key)

    return au_actualizado


def eliminar_au(db: Session, id_au: uuid.UUID, id_usuario: uuid.UUID) -> None:
    """Elimina un AU propio e invalida la cache de listado del usuario.

    Args:
        db: Sesión de base de datos.
        id_au: Identificador UUID del AU a eliminar.
        id_usuario: Identificador UUID del usuario propietario esperado.

    Raises:
        ErrorNoEncontrado: Si el AU no existe.
        AppException: Si el AU pertenece a otro usuario (403).
    """
    au: Au | None = au_repository.obtener_au_por_id(db=db, id_au=id_au)
    if not au:
        raise ErrorNoEncontrado("AU")
    if au.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para eliminar este AU.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )
    au_repository.eliminar_au(db=db, au=au)
    cache_key = _cache_key_aus(id_usuario=id_usuario)
    invalidar_cache(cache_key)

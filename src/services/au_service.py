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


def _cache_key_aus(id_usuario: uuid.UUID):
    return f"aus:usuario:{id_usuario}"


def crear_au(
    db: Session,
    id_usuario: uuid.UUID,
    nombre_au: str,
    descripcion_au: str | None = None,
) -> Au:
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
    if not nombre_au:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar el nombre del AU.")
    au: Au | None = au_repository.obtener_au_por_nombre(
        db=db, id_usuario=id_usuario, nombre_au=nombre_au
    )
    if not au:
        raise ErrorNoEncontrado("AU")
    return au


def obtener_au_por_id(db: Session, id_au: uuid.UUID, id_usuario: uuid.UUID) -> Au:
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

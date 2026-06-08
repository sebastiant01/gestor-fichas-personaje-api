import uuid
from sqlalchemy.orm import Session
from src.entities.au import Au
from src.exceptions.excepciones import (
    AppException,
    ErrorDatosInvalidos,
    ErrorNoEncontrado,
)
from src.repositories import au_repository
from fastapi import status


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
    return au_repository.crear_au(db=db, au=nuevo_au)


def obtener_aus_por_usuario(db: Session, id_usuario: uuid.UUID) -> list[Au]:
    return au_repository.obtener_aus_por_id_usuario(db=db, id_usuario=id_usuario)


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

    return au_repository.actualizar_au(db=db, au=au, datos=datos)


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

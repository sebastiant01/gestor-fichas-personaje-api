import uuid
from datetime import date

from sqlalchemy.orm import Session

from src.entities.ficha_personaje import FichaPersonaje
from src.entities.au import Au
from src.exceptions.excepciones import (
    AppException,
    ErrorDatosInvalidos,
    ErrorNoEncontrado,
)
from src.repositories import ficha_personaje_repository, au_repository

from fastapi import status


def crear_ficha_personaje(
    db: Session,
    id_usuario: uuid.UUID,
    id_au: uuid.UUID,
    nombre_personaje: str,
    sexo: str,
    fecha_cumpleanos: date,
    descripcion_personaje: str | None = None,
    edad: int | None = None,
    signo_zodiacal: str | None = None,
    url_imagen: str | None = None,
    url_musica: str | None = None,
) -> FichaPersonaje:
    if not nombre_personaje:
        raise ErrorDatosInvalidos(
            mensaje="Error: Debe ingresar un nombre para el personaje."
        )
    if not sexo:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar el sexo del personaje.")
    if not fecha_cumpleanos:
        raise ErrorDatosInvalidos(
            mensaje="Error: Debe ingresar la fecha de cumpleaños."
        )

    au: Au | None = au_repository.obtener_au_por_id(db=db, id_au=id_au)
    if not au:
        raise ErrorNoEncontrado("AU")
    if au.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para usar este AU.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )

    if edad is not None and "idols" not in au.nombre_au.lower():
        raise ErrorDatosInvalidos(
            mensaje="Error: La edad solo está permitida en el AU 'idols'."
        )
    if "idols" in au.nombre_au.lower() and edad is not None and edad <= 0:
        raise ErrorDatosInvalidos(mensaje="Error: La edad debe ser mayor a 0.")

    nueva_ficha: FichaPersonaje = FichaPersonaje(
        id_usuario=id_usuario,
        id_au=id_au,
        nombre_personaje=nombre_personaje,
        sexo=sexo,
        fecha_cumpleanos=fecha_cumpleanos,
        descripcion_personaje=descripcion_personaje,
        edad=edad,
        signo_zodiacal=signo_zodiacal,
        url_imagen=url_imagen,
        url_musica=url_musica,
    )
    return ficha_personaje_repository.crear_ficha_personaje(db=db, ficha=nueva_ficha)


def obtener_fichas_por_usuario(
    db: Session, id_usuario: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[FichaPersonaje]:
    return ficha_personaje_repository.obtener_fichas_por_id_usuario(
        db=db, id_usuario=id_usuario, skip=skip, limit=limit
    )


def obtener_ficha_por_id(
    db: Session,
    id_ficha: uuid.UUID,
    id_usuario: uuid.UUID,
) -> FichaPersonaje:
    ficha: FichaPersonaje | None = ficha_personaje_repository.obtener_ficha_por_id(
        db=db, id_ficha=id_ficha
    )
    if not ficha:
        raise ErrorNoEncontrado("Ficha de personaje")
    if ficha.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para acceder a esta ficha.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )
    return ficha


def obtener_fichas_por_au(
    db: Session,
    id_usuario: uuid.UUID,
    id_au: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[FichaPersonaje]:
    au: Au | None = au_repository.obtener_au_por_id(db=db, id_au=id_au)
    if not au:
        raise ErrorNoEncontrado("AU")
    if au.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para usar este AU.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )
    return ficha_personaje_repository.obtener_fichas_por_au(
        db=db, id_usuario=id_usuario, id_au=id_au, skip=skip, limit=limit
    )


def obtener_fichas_por_nombre_personaje(
    db: Session,
    id_usuario: uuid.UUID,
    nombre_personaje: str,
    skip: int = 0,
    limit: int = 100,
) -> list[FichaPersonaje]:
    if not nombre_personaje:
        raise ErrorDatosInvalidos(
            mensaje="Error: Debe ingresar un nombre de personaje."
        )
    return ficha_personaje_repository.obtener_fichas_por_nombre_personaje(
        db=db,
        id_usuario=id_usuario,
        nombre_personaje=nombre_personaje,
        skip=skip,
        limit=limit,
    )


def obtener_fichas_por_signo(
    db: Session,
    id_usuario: uuid.UUID,
    signo_zodiacal: str,
    skip: int = 0,
    limit: int = 100,
) -> list[FichaPersonaje]:
    if not signo_zodiacal:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar un signo zodiacal.")
    return ficha_personaje_repository.obtener_fichas_por_signo(
        db=db,
        id_usuario=id_usuario,
        signo_zodiacal=signo_zodiacal,
        skip=skip,
        limit=limit,
    )


def obtener_fichas_por_sexo(
    db: Session, id_usuario: uuid.UUID, sexo: str, skip: int = 0, limit: int = 100
) -> list[FichaPersonaje]:
    if not sexo:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar un sexo.")
    return ficha_personaje_repository.obtener_fichas_por_sexo(
        db=db, id_usuario=id_usuario, sexo=sexo, skip=skip, limit=limit
    )


def obtener_fichas_por_cumpleanos(
    db: Session,
    id_usuario: uuid.UUID,
    fecha_cumpleanos: date,
    skip: int = 0,
    limit: int = 100,
) -> list[FichaPersonaje]:
    return ficha_personaje_repository.obtener_fichas_por_cumpleanos(
        db=db,
        id_usuario=id_usuario,
        fecha_cumpleanos=fecha_cumpleanos,
        skip=skip,
        limit=limit,
    )


def obtener_fichas_por_dia_cumpleanos(
    db: Session, id_usuario: uuid.UUID, dia: int, skip: int = 0, limit: int = 100
) -> list[FichaPersonaje]:
    if dia < 1 or dia > 31:
        raise ErrorDatosInvalidos(mensaje="Error: El día debe estar entre 1 y 31.")
    return ficha_personaje_repository.obtener_fichas_por_dia_cumpleanos(
        db=db, id_usuario=id_usuario, dia=dia, skip=skip, limit=limit
    )


def obtener_fichas_por_mes_cumpleanos(
    db: Session, id_usuario: uuid.UUID, mes: int, skip: int = 0, limit: int = 100
) -> list[FichaPersonaje]:
    if mes < 1 or mes > 12:
        raise ErrorDatosInvalidos(mensaje="Error: El mes debe estar entre 1 y 12.")
    return ficha_personaje_repository.obtener_fichas_por_mes_cumpleanos(
        db=db, id_usuario=id_usuario, mes=mes, skip=skip, limit=limit
    )


def actualizar_ficha(
    db: Session, id_ficha: uuid.UUID, id_usuario: uuid.UUID, **kwargs
) -> FichaPersonaje:
    ficha: FichaPersonaje | None = ficha_personaje_repository.obtener_ficha_por_id(
        db=db, id_ficha=id_ficha
    )
    if not ficha:
        raise ErrorNoEncontrado("Ficha de personaje")
    if ficha.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para modificar esta ficha.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )

    if "id_au" in kwargs and kwargs["id_au"] is not None:
        au: Au | None = au_repository.obtener_au_por_id(db=db, id_au=kwargs["id_au"])
        if not au:
            raise ErrorNoEncontrado("AU")
        if au.id_usuario != id_usuario:
            raise AppException(
                mensaje="Error: No tienes permiso para usar este AU.",
                codigo_http=status.HTTP_403_FORBIDDEN,
            )
        au_destino = au
    else:
        au_destino = ficha.au

    if "edad" in kwargs and kwargs["edad"] is not None:
        if "idols" not in au_destino.nombre_au.lower():
            raise ErrorDatosInvalidos(
                mensaje="Error: La edad solo está permitida en el AU 'idols'."
            )
        if kwargs["edad"] <= 0:
            raise ErrorDatosInvalidos(mensaje="Error: La edad debe ser mayor a 0.")

    datos = {k: v for k, v in kwargs.items() if v is not None}
    if not datos:
        raise ErrorDatosInvalidos(
            mensaje="Error: No se enviaron datos para actualizar."
        )

    return ficha_personaje_repository.actualizar_ficha(db=db, ficha=ficha, datos=datos)


def eliminar_ficha(db: Session, id_ficha: uuid.UUID, id_usuario: uuid.UUID) -> None:
    ficha: FichaPersonaje | None = ficha_personaje_repository.obtener_ficha_por_id(
        db=db, id_ficha=id_ficha
    )
    if not ficha:
        raise ErrorNoEncontrado("Ficha de personaje")
    if ficha.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para eliminar esta ficha.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )
    ficha_personaje_repository.eliminar_ficha(db=db, ficha=ficha)

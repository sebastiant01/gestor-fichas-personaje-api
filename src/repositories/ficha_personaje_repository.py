"""
Capa de acceso a datos para ``FichaPersonaje``.

Incluye consultas filtradas por usuario, AU, cumpleaños y metadatos del personaje.
"""

from typing import Optional

import uuid
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import select, extract

from src.entities.ficha_personaje import FichaPersonaje


def crear_ficha_personaje(db: Session, ficha: FichaPersonaje) -> FichaPersonaje:
    """Persiste una ficha nueva."""
    db.add(ficha)
    db.commit()
    db.refresh(ficha)
    return ficha


def obtener_fichas_por_id_usuario(
    db: Session,
    id_usuario: uuid.UUID,
    skip: int,
    limit: int,
    orden_por: Optional[str] = None,
) -> list[FichaPersonaje]:
    """Todas las fichas del usuario, paginadas."""
    query = db.query(FichaPersonaje).filter(FichaPersonaje.id_usuario == id_usuario)

    if orden_por == "desc":
        query = query.order_by(FichaPersonaje.fecha_creacion.desc())
    elif orden_por == "asc":
        query = query.order_by(FichaPersonaje.fecha_creacion.asc())

    return query.offset(skip).limit(limit).all()


def obtener_ficha_por_id(db: Session, id_ficha: uuid.UUID) -> FichaPersonaje | None:
    """Ficha por clave primaria (sin filtro de propietario)."""
    return (
        db.query(FichaPersonaje)
        .filter(FichaPersonaje.id_ficha_personaje == id_ficha)
        .first()
    )


def obtener_fichas_por_au(
    db: Session, id_usuario: uuid.UUID, id_au: uuid.UUID, skip: int, limit: int
) -> list[FichaPersonaje]:
    """Fichas de un AU concreto pertenecientes al usuario."""
    return (
        db.query(FichaPersonaje)
        .filter(FichaPersonaje.id_usuario == id_usuario, FichaPersonaje.id_au == id_au)
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_fichas_por_nombre_personaje(
    db: Session, id_usuario: uuid.UUID, nombre_personaje: str, skip: int, limit: int
) -> list[FichaPersonaje]:
    """Fichas cuyo ``nombre_personaje`` coincide (puede haber varias en distintos AUs)."""
    return (
        db.query(FichaPersonaje)
        .filter(
            FichaPersonaje.id_usuario == id_usuario,
            FichaPersonaje.nombre_personaje == nombre_personaje,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_fichas_por_signo(
    db: Session, id_usuario: uuid.UUID, signo_zodiacal: str, skip: int, limit: int
) -> list[FichaPersonaje]:
    """Fichas filtradas por signo zodiacal."""
    return (
        db.query(FichaPersonaje)
        .filter(
            FichaPersonaje.id_usuario == id_usuario,
            FichaPersonaje.signo_zodiacal == signo_zodiacal,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_fichas_por_sexo(
    db: Session, id_usuario: uuid.UUID, sexo: str, skip: int, limit: int
) -> list[FichaPersonaje]:
    """Fichas filtradas por sexo."""
    return (
        db.query(FichaPersonaje)
        .filter(
            FichaPersonaje.id_usuario == id_usuario,
            FichaPersonaje.sexo == sexo,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_fichas_por_cumpleanos(
    db: Session, id_usuario: uuid.UUID, fecha_cumpleanos: date, skip: int, limit: int
) -> list[FichaPersonaje]:
    """Fichas con ``fecha_cumpleanos`` exacta."""
    return (
        db.query(FichaPersonaje)
        .filter(
            FichaPersonaje.id_usuario == id_usuario,
            FichaPersonaje.fecha_cumpleanos == fecha_cumpleanos,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_fichas_por_dia_cumpleanos(
    db: Session, id_usuario: uuid.UUID, dia: int, skip: int, limit: int
) -> list[FichaPersonaje]:
    """Fichas cuyo día del mes de cumpleaños coincide (1–31)."""
    statement = (
        select(FichaPersonaje)
        .where(
            extract("day", FichaPersonaje.fecha_cumpleanos) == dia,
            FichaPersonaje.id_usuario == id_usuario,
        )
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement=statement).all())


def obtener_fichas_por_mes_cumpleanos(
    db: Session, id_usuario: uuid.UUID, mes: int, skip: int, limit: int
) -> list[FichaPersonaje]:
    """Fichas cuyo mes de cumpleaños coincide (1–12)."""
    statement = (
        select(FichaPersonaje)
        .where(
            extract("month", FichaPersonaje.fecha_cumpleanos) == mes,
            FichaPersonaje.id_usuario == id_usuario,
        )
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement=statement).all())


def actualizar_ficha(db: Session, ficha: FichaPersonaje, datos: dict) -> FichaPersonaje:
    """Actualiza campos de la ficha."""
    for campo, valor in datos.items():
        setattr(ficha, campo, valor)
    db.commit()
    db.refresh(ficha)
    return ficha


def eliminar_ficha(db: Session, ficha: FichaPersonaje) -> None:
    """Elimina la ficha de la base de datos."""
    db.delete(ficha)
    db.commit()


def limpiar_imagen(db: Session, ficha: FichaPersonaje) -> None:
    """Pone ``url_imagen`` en ``None`` sin borrar la fila."""
    ficha.url_imagen = None
    db.commit()
    db.refresh(ficha)

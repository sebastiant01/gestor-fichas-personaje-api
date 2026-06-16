from typing import Optional
import uuid
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import select, extract

from src.entities.ficha_personaje import FichaPersonaje


def crear_ficha_personaje(db: Session, ficha: FichaPersonaje) -> FichaPersonaje:
    db.add(ficha)
    db.commit()
    db.refresh(ficha)
    return ficha


def obtener_fichas_por_id_usuario(
    db: Session, id_usuario: uuid.UUID
) -> list[FichaPersonaje]:
    return (
        db.query(FichaPersonaje).filter(FichaPersonaje.id_usuario == id_usuario).all()
    )


def obtener_ficha_por_id(db: Session, id_ficha: uuid.UUID) -> FichaPersonaje | None:
    return (
        db.query(FichaPersonaje)
        .filter(FichaPersonaje.id_ficha_personaje == id_ficha)
        .first()
    )


def obtener_fichas_por_au(
    db: Session, id_usuario: uuid.UUID, id_au: uuid.UUID
) -> list[FichaPersonaje]:
    return (
        db.query(FichaPersonaje)
        .filter(FichaPersonaje.id_usuario == id_usuario, FichaPersonaje.id_au == id_au)
        .all()
    )


def obtener_fichas_por_nombre_personaje(
    db: Session, id_usuario: uuid.UUID, nombre_personaje: str
) -> list[FichaPersonaje]:
    return (
        db.query(FichaPersonaje)
        .filter(
            FichaPersonaje.id_usuario == id_usuario,
            FichaPersonaje.nombre_personaje == nombre_personaje,
        )
        .all()
    )


def obtener_fichas_por_signo(
    db: Session, id_usuario: uuid.UUID, signo_zodiacal: str
) -> list[FichaPersonaje]:
    return (
        db.query(FichaPersonaje)
        .filter(
            FichaPersonaje.id_usuario == id_usuario,
            FichaPersonaje.signo_zodiacal == signo_zodiacal,
        )
        .all()
    )


def obtener_fichas_por_sexo(
    db: Session, id_usuario: uuid.UUID, sexo: str
) -> list[FichaPersonaje]:
    return (
        db.query(FichaPersonaje)
        .filter(
            FichaPersonaje.id_usuario == id_usuario,
            FichaPersonaje.sexo == sexo,
        )
        .all()
    )


def obtener_fichas_por_cumpleanos(
    db: Session, id_usuario: uuid.UUID, fecha_cumpleanos: date
) -> list[FichaPersonaje]:
    return (
        db.query(FichaPersonaje)
        .filter(
            FichaPersonaje.id_usuario == id_usuario,
            FichaPersonaje.fecha_cumpleanos == fecha_cumpleanos,
        )
        .all()
    )


def obtener_fichas_por_dia_cumpleanos(
    db: Session, id_usuario: uuid.UUID, dia: int
) -> list[FichaPersonaje]:
    statement = select(FichaPersonaje).where(
        extract("day", FichaPersonaje.fecha_cumpleanos) == dia,
        FichaPersonaje.id_usuario == id_usuario,
    )
    return list(db.scalars(statement=statement).all())


def obtener_fichas_por_mes_cumpleanos(
    db: Session, id_usuario: uuid.UUID, mes: int
) -> list[FichaPersonaje]:
    statement = select(FichaPersonaje).where(
        extract("month", FichaPersonaje.fecha_cumpleanos) == mes,
        FichaPersonaje.id_usuario == id_usuario,
    )
    return list(db.scalars(statement=statement).all())


def actualizar_ficha(db: Session, ficha: FichaPersonaje, datos: dict) -> FichaPersonaje:
    for campo, valor in datos.items():
        setattr(ficha, campo, valor)
    db.commit()
    db.refresh(ficha)
    return ficha


def eliminar_ficha(db: Session, ficha: FichaPersonaje) -> None:
    db.delete(ficha)
    db.commit()

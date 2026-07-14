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
    db: Session, id_usuario: uuid.UUID, skip: int, limit: int
) -> list[FichaPersonaje]:
    return (
        db.query(FichaPersonaje)
        .filter(FichaPersonaje.id_usuario == id_usuario)
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_ficha_por_id(db: Session, id_ficha: uuid.UUID) -> FichaPersonaje | None:
    return (
        db.query(FichaPersonaje)
        .filter(FichaPersonaje.id_ficha_personaje == id_ficha)
        .first()
    )


def obtener_fichas_por_au(
    db: Session, id_usuario: uuid.UUID, id_au: uuid.UUID, skip: int, limit: int
) -> list[FichaPersonaje]:
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
    for campo, valor in datos.items():
        setattr(ficha, campo, valor)
    db.commit()
    db.refresh(ficha)
    return ficha


def eliminar_ficha(db: Session, ficha: FichaPersonaje) -> None:
    db.delete(ficha)
    db.commit()


def limpiar_imagen(db: Session, ficha: FichaPersonaje) -> None:
    ficha.url_imagen = None
    db.commit()
    db.refresh(ficha)

"""
Capa de acceso a datos para ``Au`` (universos alternos).
"""

import uuid

from sqlalchemy.orm import Session

from src.entities.au import Au


def crear_au(db: Session, au: Au) -> Au:
    """Inserta un AU y devuelve la instancia con ID asignado."""
    db.add(au)
    db.commit()
    db.refresh(au)
    return au


def obtener_au_por_id(db: Session, id_au: uuid.UUID) -> Au | None:
    """Obtiene un AU por ``id_au``."""
    return db.query(Au).filter(Au.id_au == id_au).first()


def obtener_aus_por_id_usuario(
    db: Session, id_usuario: uuid.UUID, skip: int, limit: int
) -> list[Au]:
    """Lista AUs de un usuario con paginación ``skip``/``limit``."""
    return (
        db.query(Au).filter(Au.id_usuario == id_usuario).offset(skip).limit(limit).all()
    )


def obtener_au_por_nombre(
    db: Session, id_usuario: uuid.UUID, nombre_au: str
) -> Au | None:
    """Busca un AU por nombre dentro del ámbito de un usuario."""
    return (
        db.query(Au)
        .filter(Au.id_usuario == id_usuario, Au.nombre_au == nombre_au)
        .first()
    )


def actualizar_au(db: Session, au: Au, datos: dict) -> Au:
    """Actualiza campos del AU según ``datos``."""
    for campo, valor in datos.items():
        setattr(au, campo, valor)
    db.commit()
    db.refresh(au)
    return au


def eliminar_au(db: Session, au: Au) -> None:
    """Elimina un AU (puede fallar por FK si tiene fichas asociadas)."""
    db.delete(au)
    db.commit()

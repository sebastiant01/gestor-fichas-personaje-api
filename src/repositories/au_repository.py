import uuid

from sqlalchemy.orm import Session

from src.entities.au import Au


def crear_au(db: Session, au: Au) -> Au:
    db.add(au)
    db.commit()
    db.refresh(au)
    return au


def obtener_au_por_id(db: Session, id_au: uuid.UUID) -> Au | None:
    return db.query(Au).filter(Au.id_au == id_au).first()


def obtener_aus_por_id_usuario(
    db: Session, id_usuario: uuid.UUID, skip: int, limit: int
) -> list[Au]:
    return (
        db.query(Au).filter(Au.id_usuario == id_usuario).offset(skip).limit(limit).all()
    )


def obtener_au_por_nombre(
    db: Session, id_usuario: uuid.UUID, nombre_au: str
) -> Au | None:
    return (
        db.query(Au)
        .filter(Au.id_usuario == id_usuario, Au.nombre_au == nombre_au)
        .first()
    )


def actualizar_au(db: Session, au: Au, datos: dict) -> Au:
    for campo, valor in datos.items():
        setattr(au, campo, valor)
    db.commit()
    db.refresh(au)
    return au


def eliminar_au(db: Session, au: Au) -> None:
    db.delete(au)
    db.commit()

from typing import Optional
import uuid

from sqlalchemy.orm import Session

from src.entities.usuario import Usuario


def crear_usuario(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def obtener_usuarios(db: Session, skip: int, limit: int) -> list[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()


def obtener_usuario_por_id(db: Session, id_usuario: uuid.UUID) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()


def obtener_usuario_por_nombre_usuario(
    db: Session, nombre_usuario: str
) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first()


def actualizar_usuario(db: Session, usuario: Usuario, datos: dict) -> Usuario:
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario: Usuario) -> None:
    db.delete(usuario)
    db.commit()

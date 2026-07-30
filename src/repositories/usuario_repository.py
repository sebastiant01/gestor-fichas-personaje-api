"""
Capa de acceso a datos para ``Usuario``.

Funciones puras que reciben una ``Session``; no contienen reglas de negocio.
"""

import uuid

from sqlalchemy.orm import Session

from src.entities.usuario import Usuario


def crear_usuario(db: Session, usuario: Usuario) -> Usuario:
    """Persiste un usuario nuevo y devuelve la fila refrescada."""
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def obtener_usuario_por_id(db: Session, id_usuario: uuid.UUID) -> Usuario | None:
    """Busca un usuario por clave primaria."""
    return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()


def obtener_usuario_por_nombre_usuario(
    db: Session, nombre_usuario: str
) -> Usuario | None:
    """Busca un usuario por ``nombre_usuario`` único."""
    return db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first()


def actualizar_usuario(db: Session, usuario: Usuario, datos: dict) -> Usuario:
    """Aplica ``datos`` al modelo, confirma transacción y refresca."""
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario: Usuario) -> None:
    """Elimina el usuario de la base de datos."""
    db.delete(usuario)
    db.commit()

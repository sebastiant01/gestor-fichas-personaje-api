"""
Reglas de negocio para usuarios: registro, consulta y actualización.

Valida contraseñas, evita duplicados y delega persistencia al repositorio.
"""

from typing import Optional
import uuid
from src.entities.usuario import Usuario
from sqlalchemy.orm import Session
from src.exceptions.excepciones import (
    ErrorDatosInvalidos,
    AppException,
    ErrorNoEncontrado,
)
from src.repositories import usuario_repository
from src.utils.hash_password import hash_password
from fastapi import status


def crear_usuario(db: Session, nombre_usuario: str, contrasena: str) -> Usuario:
    """Registra un usuario con contraseña hasheada; 409 si el nombre ya existe."""
    if not nombre_usuario:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar un nombre.")
    if not contrasena:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar una contraseña.")
    if len(contrasena) <= 5:
        raise ErrorDatosInvalidos(
            mensaje="Error: Debe haber una contraseña mayor a 5 caracteres."
        )
    if not contrasena.isalnum():
        raise ErrorDatosInvalidos(
            mensaje="Error: La contraseña debe tener letras y números."
        )

    usuario_existente: Optional[Usuario] = (
        usuario_repository.obtener_usuario_por_nombre_usuario(
            db=db, nombre_usuario=nombre_usuario
        )
    )
    if usuario_existente:
        raise AppException(
            mensaje="Error: Este usuario ya existe.",
            codigo_http=status.HTTP_409_CONFLICT,
        )
    contrasena_hash: str = hash_password(contrasena)

    nuevo_usuario: Usuario = Usuario(
        nombre_usuario=nombre_usuario, contrasena_hash=contrasena_hash
    )

    return usuario_repository.crear_usuario(db=db, usuario=nuevo_usuario)


def obtener_usuario_por_id(db: Session, id_usuario: uuid.UUID) -> Optional[Usuario]:
    """Devuelve el usuario o lanza ``ErrorNoEncontrado``."""
    if not isinstance(id_usuario, uuid.UUID):
        raise ErrorDatosInvalidos(mensaje="Error: El id es inválido.")
    if not id_usuario:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar un id de usuario.")

    usuario: Usuario | None = usuario_repository.obtener_usuario_por_id(
        db=db, id_usuario=id_usuario
    )
    if not usuario:
        raise ErrorNoEncontrado("Usuario")
    return usuario


def obtener_usuario_por_nombre_usuario(db: Session, nombre_usuario: str) -> Usuario:
    """Busca por nombre de login; usado en autenticación."""
    if len(nombre_usuario) == 0:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar un nombre de usuario.")
    usuario: Usuario | None = usuario_repository.obtener_usuario_por_nombre_usuario(
        db=db, nombre_usuario=nombre_usuario
    )
    if not usuario:
        raise ErrorNoEncontrado("Usuario")
    return usuario


def actualizar_usuario(db: Session, id_usuario: uuid.UUID, **kwargs) -> Usuario:
    """Actualiza campos no nulos; re-hashea si llega ``contrasena``."""
    usuario: Optional[Usuario] = usuario_repository.obtener_usuario_por_id(
        db, id_usuario
    )
    if not usuario:
        raise ErrorNoEncontrado("Usuario")

    if "contrasena" in kwargs and kwargs["contrasena"] is not None:
        kwargs["contrasena_hash"] = hash_password(kwargs.pop("contrasena"))

    datos = {key: value for key, value in kwargs.items() if value is not None}
    if not datos:
        raise ErrorDatosInvalidos(
            mensaje="Error: No se enviaron datos para actualizar."
        )
    return usuario_repository.actualizar_usuario(db, usuario, datos)


def eliminar_usuario(db: Session, id_usuario: uuid.UUID) -> None:
    """Elimina la cuenta si existe."""
    usuario: Optional[Usuario] = usuario_repository.obtener_usuario_por_id(
        db, id_usuario
    )
    if not usuario:
        raise ErrorNoEncontrado("Usuario")
    usuario_repository.eliminar_usuario(db, usuario)

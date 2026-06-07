from typing import Optional
from src.entities.usuario import Usuario
from sqlalchemy.orm import Session
from src.exceptions.excepciones import ErrorDatosInvalidos, AppException
from src.repositories import usuario_repository
from src.utils.hash_password import hash_password
from fastapi import status


def crear_usuario(db: Session, nombre_usuario: str, contrasena: str) -> None:
    if len(nombre_usuario) == 0:
        raise ErrorDatosInvalidos(mensaje="Error: Debe haber nombre de usuario válido.")
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
            codigo_http=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    contrasena_hash: str = hash_password(contrasena)

    nuevo_usuario: Usuario = Usuario(
        nombre_usuario=nombre_usuario, contrasena_hash=contrasena_hash
    )

    usuario_repository.crear_usuario(db=db, usuario=nuevo_usuario)

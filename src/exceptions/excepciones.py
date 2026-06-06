"""En esta clase se encuentran las excepciones personalizadas de la app."""

from typing import Any, Dict

from fastapi import status


class AppException(Exception):
    def __init__(self, mensaje, codigo_http=status.HTTP_400_BAD_REQUEST, headers=None):
        self.mensaje = mensaje
        self.codigo_http = codigo_http
        self.headers = headers
        super().__init__(self.mensaje)


class ErrorNoEncontrado(AppException):
    def __init__(self, entidad: str):
        super().__init__(
            mensaje=f"{entidad} no encontrado/a", codigo_http=status.HTTP_404_NOT_FOUND
        )


class ErrorDatosInvalidos(AppException):
    def __init__(self):
        super().__init__(
            mensaje="Error: Los datos ingresados no son válidos.",
        )


class ErrorNoAutorizadoJWT(AppException):
    def __init__(
        self,
        mensaje: str = "Error: Acceso restringido",
        headers: Dict[str, Any] | None = None,
    ):
        super().__init__(
            mensaje=mensaje,
            codigo_http=status.HTTP_401_UNAUTHORIZED,
            headers=headers,
        )

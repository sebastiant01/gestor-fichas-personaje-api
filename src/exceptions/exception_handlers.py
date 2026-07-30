"""Registro de manejadores globales de excepciones para respuestas JSON coherentes."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import ResponseValidationError, RequestValidationError
from src.exceptions.excepciones import AppException


def registrar_error_handlers(app: FastAPI) -> None:
    """
    Registra los manejadores de errores globales en la instancia de FastAPI.

    Cada handler captura un tipo de excepción y retorna una respuesta JSON
    uniforme con los campos `exito`, `mensaje` y, cuando aplica, `detalles`.

    Args:
        app: Instancia de la aplicación FastAPI sobre la que se registran
             los handlers.
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """
        Maneja errores de validación en el body de la petición.

        Se activa cuando Pydantic detecta que el JSON enviado por el cliente
        es inválido: campos faltantes, tipos de datos incorrectos, etc.
        Construye una lista de detalles con el campo afectado y el motivo
        del fallo para facilitar la corrección en el cliente.

        Retorna HTTP 422 con el campo `detalles` como lista de objetos
        `{campo, mensaje}`.
        """
        detalles = []
        for error in exc.errors():
            detalles.append(
                {"campo": " -> ".join(map(str, error["loc"])), "mensaje": error["msg"]}
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "exito": False,
                "mensaje": "El cuerpo de la petición (body) no es válido.",
                "detalles": detalles,
            },
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """
        Maneja excepciones de dominio derivadas de AppException.

        Retorna el código HTTP y el mensaje definidos en la excepción,
        lo que permite que cada subclase controle su propia respuesta
        (por ejemplo, NoEncontradoError → 404, DatosInvalidosError → 400).
        """
        return JSONResponse(
            status_code=exc.codigo_http,
            content={
                "exito": False,
                "mensaje": exc.mensaje,
            },
            headers=exc.headers,
        )

    @app.exception_handler(ResponseValidationError)
    async def validation_response_error_handler(
        request: Request, exc: ResponseValidationError
    ):
        """
        Maneja errores de validación en la respuesta generada por el servidor.

        Se activa cuando el objeto retornado por un endpoint no satisface
        el esquema Pydantic declarado en `response_model`, lo que indica
        una inconsistencia entre el modelo ORM y el esquema de salida.
        Incluye el detalle crudo de la excepción para facilitar el diagnóstico
        en desarrollo.

        Retorna HTTP 500 con el campo `detalles` como string descriptivo.
        """
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "exito": False,
                "mensaje": "Error: La base de datos devolvió campos que el esquema no reconoce o faltan campos obligatorios.",
                "detalles": str(exc),
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """
        Maneja errores de valor no capturados por Pydantic ni por AppException.

        Actúa como red de seguridad para ValueError lanzados directamente
        en lógica de negocio que no usen la jerarquía de AppException.
        Retorna siempre HTTP 400 con el mensaje de la excepción.
        """
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "exito": False,
                "mensaje": str(exc),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Maneja cualquier excepción no prevista por los handlers anteriores.

        Actúa como último recurso para errores inesperados. Retorna un
        mensaje genérico para no exponer detalles internos al cliente.
        Retorna HTTP 500.
        """
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "exito": False,
                "mensaje": "Error interno del servidor",
            },
        )

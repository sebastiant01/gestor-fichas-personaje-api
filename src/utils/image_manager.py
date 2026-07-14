from typing import Any

from src.exceptions.excepciones import AppException

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from fastapi import status

import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME", ""),
    api_key=os.getenv("CLOUDINARY_API_KEY", ""),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
    secure=True,
)

TIPOS_PERMITIDOS = ["image/jpg", "image/jpeg", "image/png", "image/webp"]


def subir_imagen(imagen, public_id: str | None = None) -> str:
    resultado = cloudinary.uploader.upload(
        file=imagen,
        folder="fichas_personajes",
        public_id=public_id,
        overwrite=True,
        invalidate=True,
    )
    return resultado["secure_url"]


def eliminar_imagen(public_id: str) -> None:
    if not public_id:
        raise AppException(
            mensaje="No se incluyó el public id del archivo.",
            codigo_http=status.HTTP_400_BAD_REQUEST,
        )
    resultado: dict[str, str] = cloudinary.uploader.destroy(
        public_id=public_id, invalidate=True
    )
    if resultado.get("result") not in ["ok", "not found"]:
        raise AppException(
            mensaje="No se pudo remover la imagen.",
            codigo_http=status.HTTP_502_BAD_GATEWAY,
        )

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from fastapi import UploadFile, HTTPException, status

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

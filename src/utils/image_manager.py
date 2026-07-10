import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from fastapi import UploadFile

import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME", ""),
    api_key=os.getenv("CLOUDINARY_API_KEY", ""),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
    secure=True,
)


def subir_imagen(imagen) -> str:
    resultado = cloudinary.uploader.upload(imagen)
    return resultado["secure_url"]

"""
Esquemas Pydantic para usuarios (entrada y salida API).

``UsuarioResponse`` omite la contraseña; el hash nunca se expone.
"""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field


class UsuarioCreate(BaseModel):
    """Datos para registrar un usuario administrador."""

    nombre_usuario: str = Field(..., min_length=1, max_length=40)
    contrasena: str = Field(..., min_length=6, max_length=15)


class UsuarioUpdate(BaseModel):
    """Campos opcionales para ``PATCH /usuarios/me``."""

    nombre_usuario: Optional[str] = Field(None, min_length=1, max_length=40)
    contrasena: Optional[str] = Field(None, min_length=6)


class UsuarioResponse(BaseModel):
    """Representación pública de un usuario."""

    id_usuario: uuid.UUID
    nombre_usuario: str
    es_admin: bool

    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field


class UsuarioCreate(BaseModel):
    nombre_usuario: str = Field(..., min_length=1, max_length=40)
    contrasena: str = Field(..., min_length=6, max_length=15)


class UsuarioUpdate(BaseModel):
    nombre_usuario: Optional[str] = Field(None, min_length=1, max_length=40)
    contrasena: Optional[str] = Field(None, min_length=6)


class UsuarioResponse(BaseModel):
    id_usuario: uuid.UUID
    nombre_usuario: str
    es_admin: bool

    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

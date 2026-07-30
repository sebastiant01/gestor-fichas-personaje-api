"""
Esquemas Pydantic para universos alternos (AUs).
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuCreate(BaseModel):
    """Cuerpo de ``POST /aus``."""

    nombre_au: str = Field(..., min_length=1, max_length=50)
    descripcion_au: Optional[str] = Field(None, max_length=500)


class AuUpdate(BaseModel):
    """Cuerpo de ``PATCH /aus/{id_au}``."""

    nombre_au: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion_au: Optional[str] = Field(None, max_length=500)


class AuResponse(BaseModel):
    """AU tal como se expone en la API."""

    id_au: UUID
    id_usuario: UUID

    nombre_au: str
    descripcion_au: Optional[str] = None

    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

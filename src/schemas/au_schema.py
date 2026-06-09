from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuCreate(BaseModel):
    nombre_au: str = Field(..., min_length=1, max_length=50)
    descripcion_au: Optional[str] = Field(None, max_length=500)


class AuUpdate(BaseModel):
    nombre_au: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion_au: Optional[str] = Field(None, max_length=500)


class AuResponse(BaseModel):
    id_au: UUID
    id_usuario: UUID

    nombre_au: str
    descripcion_au: Optional[str] = None

    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

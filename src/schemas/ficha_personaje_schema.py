"""
Esquemas Pydantic para fichas de personaje.

``id_usuario`` no aparece en Create/Update: se toma del JWT en el router.
"""

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class FichaPersonajeCreate(BaseModel):
    """Datos para crear una ficha; ``id_au`` es obligatorio."""

    id_au: UUID

    nombre_personaje: str = Field(..., min_length=1, max_length=100)
    sexo: str = Field(..., min_length=1, max_length=30)
    fecha_cumpleanos: date
    edad: Optional[int] = Field(None, gt=0)
    signo_zodiacal: Optional[str] = Field(None, max_length=20)
    descripcion_personaje: Optional[str] = None
    url_imagen: Optional[str] = None
    url_musica: Optional[str] = None


class FichaPersonajeUpdate(BaseModel):
    """Actualización parcial de ficha."""

    id_au: Optional[UUID] = None

    nombre_personaje: Optional[str] = Field(None, min_length=1, max_length=100)
    sexo: Optional[str] = Field(None, min_length=1, max_length=30)
    fecha_cumpleanos: Optional[date] = None
    edad: Optional[int] = Field(None, gt=0)
    signo_zodiacal: Optional[str] = Field(None, max_length=20)
    descripcion_personaje: Optional[str] = None
    url_imagen: Optional[str] = None
    url_musica: Optional[str] = None


class FichaPersonajeResponse(BaseModel):
    """Ficha serializada para respuestas HTTP."""

    id_ficha_personaje: UUID
    id_au: UUID
    id_usuario: UUID

    nombre_personaje: str
    sexo: str
    fecha_cumpleanos: date
    edad: Optional[int] = None
    signo_zodiacal: Optional[str] = None
    descripcion_personaje: Optional[str] = None
    url_imagen: Optional[str] = None
    url_musica: Optional[str] = None

    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

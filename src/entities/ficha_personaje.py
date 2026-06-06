from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from src.entities.au import Au
from src.entities.usuario import Usuario
from src.database.base import Base
from sqlalchemy import (
    DateTime,
    Date,
    String,
    Text,
    ForeignKey,
    SmallInteger,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from src.entities.usuario import Usuario
    from src.entities.au import Au


class FichaPersonaje(Base):
    __tablename__: str = "fichas_personajes"

    id_ficha_personaje: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    id_usuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    id_au: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aus.id_au"), nullable=False
    )
    nombre_personaje: Mapped[str] = mapped_column(String(100))
    sexo: Mapped[str] = mapped_column(String(30))
    edad: Mapped[int | None] = mapped_column(SmallInteger)
    fecha_cumpleanos: Mapped[date] = mapped_column(Date)
    signo_zodiacal: Mapped[str | None] = mapped_column(String(20))
    descripcion_personaje: Mapped[str | None] = mapped_column(Text)
    url_imagen: Mapped[str | None] = mapped_column(Text)
    url_musica: Mapped[str | None] = mapped_column(Text)

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fecha_edicion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    usuario: Mapped[Usuario] = relationship(
        "Usuario", back_populates="ficha_personaje", foreign_keys=[id_usuario]
    )
    au: Mapped[Au] = relationship("Au", back_populates="fichas", foreign_keys=[id_au])

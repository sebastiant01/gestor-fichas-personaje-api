from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from src.database.base import Base
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from src.entities.au import Au
    from src.entities.ficha_personaje import FichaPersonaje


class Usuario(Base):
    __tablename__: str = "usuarios"

    id_usuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    nombre_usuario: Mapped[str] = mapped_column(String(40), unique=True)
    contrasena_hash: Mapped[str] = mapped_column(Text)
    es_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fecha_edicion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    au: Mapped[list[Au]] = relationship(
        "Au", back_populates="usuario", foreign_keys="Au.id_usuario"
    )
    ficha_personaje: Mapped[list[FichaPersonaje]] = relationship(
        "FichaPersonaje",
        back_populates="usuario",
        foreign_keys="FichaPersonaje.id_usuario",
    )

    def __init__(
        self, nombre_usuario: str, contrasena_hash: str, es_admin: bool = False
    ):
        self.nombre_usuario = nombre_usuario
        self.contrasena_hash = contrasena_hash
        self.es_admin = es_admin

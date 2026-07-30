"""
Modelo ORM de la tabla ``aus`` (universos alternos).

Cada AU pertenece a un usuario; el par (usuario, nombre_au) es único.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from src.database.base import Base
from sqlalchemy import DateTime, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from src.entities.usuario import Usuario
    from src.entities.ficha_personaje import FichaPersonaje


class Au(Base):
    """Universo alterno donde se agrupan fichas de personaje."""

    __tablename__: str = "aus"
    __table_args__ = (
        UniqueConstraint("id_usuario", "nombre_au", name="uq_au_usuario_nombre"),
    )

    id_au: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    id_usuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    nombre_au: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion_au: Mapped[str | None] = mapped_column(Text, nullable=True)

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fecha_edicion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    usuario: Mapped[Usuario] = relationship(
        "Usuario", back_populates="au", foreign_keys=[id_usuario]
    )
    fichas: Mapped[list[FichaPersonaje]] = relationship(
        "FichaPersonaje", back_populates="au", foreign_keys="FichaPersonaje.id_au"
    )

    def __init__(
        self, id_usuario: uuid.UUID, nombre_au: str, descripcion_au: str | None = None
    ):
        """Crea un AU asociado al ``id_usuario`` indicado."""
        self.id_usuario = id_usuario
        self.nombre_au = nombre_au
        self.descripcion_au = descripcion_au

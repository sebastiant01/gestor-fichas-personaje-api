import uuid
from datetime import datetime

from src.database.base import Base
from sqlalchemy import DateTime, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func


class Au(Base):
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
    descripcion_au: Mapped[str | None] = mapped_column(Text)

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fecha_edicion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    usuario: Mapped[Usuario] = relationship(  # type: ignore
        "Usuario", back_populates="aus", foreign_keys=[id_usuario]
    )
    fichas: Mapped[list[FichaPersonaje]] = relationship(  # type: ignore
        "FichaPersonaje", back_populates="au", foreign_keys="FichaPersonaje.id_au"
    )

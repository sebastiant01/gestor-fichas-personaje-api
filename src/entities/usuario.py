import uuid
from datetime import datetime

from src.database.base import Base
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func


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

    au: Mapped[list["Au"]] = relationship(  # type: ignore
        "Au", back_populates="usuario", foreign_keys="Au.id_usuario"
    )
    ficha_personaje: Mapped[list["FichaPersonaje"]] = relationship(  # type: ignore
        "FichaPersonaje",
        back_populates="usuario",
        foreign_keys="FichaPersonaje.id_usuario",
    )

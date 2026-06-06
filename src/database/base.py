from sqlalchemy.orm import DeclarativeBase
from src.database.engine import engine


class Base(DeclarativeBase):
    pass


def crear_tablas() -> None:
    """
    Crea todas las tablas en la base de datos.
    Si ya están creadas, no se verán afectadas.
    """
    Base.metadata.create_all(bind=engine)

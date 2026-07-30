"""Fábrica de sesiones y dependencia ``get_db`` para FastAPI."""

from typing import Iterator

from sqlalchemy.orm import sessionmaker, Session
from src.database.engine import engine

session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Iterator[Session]:
    """
    Abre una sesión por petición y la cierra al finalizar.

    Yields:
        Session: Sesión de SQLAlchemy ligada al motor configurado.
    """
    db: Session = session_local()

    try:
        yield db
    finally:
        db.close()

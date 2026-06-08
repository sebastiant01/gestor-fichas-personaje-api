from typing import Iterator

from sqlalchemy.orm import sessionmaker, Session
from src.database.engine import engine

session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Iterator[Session]:
    """
    Generador de sesiones de la base de datos.
    """
    db: Session = session_local()

    try:
        yield db
    finally:
        db.close()

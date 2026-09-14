"""
Fabricación de la aplicación FastAPI «Coche Biblioteca».

Este módulo debe residir en la raíz del proyecto para que Uvicorn resuelva
``api_config:app`` correctamente. Registra CORS, manejadores de errores,
el ciclo de vida (creación de tablas al arranque) y todos los routers.
"""

from sqlalchemy import text
from src.database.engine import engine
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database.base import crear_tablas

from src.routers import auth_router
from src.routers import usuario_router
from src.routers import au_router
from src.routers import ficha_personaje_router
from src.exceptions.exception_handlers import registrar_error_handlers

tags_metadata: list[dict[str, str]] = [
    {
        "name": "Auth",
        "description": "Manejo de autenticación (login) del usuario y generación de tokens JWT.",
    },
    {
        "name": "Usuarios",
        "description": "Métodos HTTP con usuarios. Por el momento solo disponible para admins.",
    },
    {
        "name": "AUs",
        "description": "Administración y manejo de AUs (Universos Alternos).",
    },
    {
        "name": "Fichas de personaje",
        "description": "Administración y manejo de fichas de personajes e imágenes.",
    },
]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Inicializa recursos al arrancar la app (p. ej. metadatos ORM en BD)."""
    from src.entities.usuario import Usuario
    from src.entities.au import Au
    from src.entities.ficha_personaje import FichaPersonaje

    crear_tablas()

    with engine.connect() as db:
        db.execute(text("SELECT 1"))

    yield
    engine.dispose()


app: FastAPI = FastAPI(
    title="Coche Biblioteca",
    version="1.0.0",
    summary='API REST del proyecto "Coche Biblioteca"',
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://coche-biblioteca-70aa7.web.app",
    ],  # URL de Angular en desarrollo y app desplegada
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_error_handlers(app=app)

app.include_router(router=auth_router.auth_router)
app.include_router(router=usuario_router.usuario_router)
app.include_router(router=au_router.au_router)
app.include_router(router=ficha_personaje_router.ficha_router)

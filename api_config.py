from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database.base import crear_tablas

from src.routers import auth_router
from src.routers import usuario_router
from src.routers import au_router
from src.routers import ficha_personaje_router
from src.exceptions.exception_handlers import registrar_error_handlers


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from src.entities.usuario import Usuario
    from src.entities.au import Au
    from src.entities.ficha_personaje import FichaPersonaje

    crear_tablas()
    yield


app: FastAPI = FastAPI(title="Coche Biblioteca", version="1.0.0")

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

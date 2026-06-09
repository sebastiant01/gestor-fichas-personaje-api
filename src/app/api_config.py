from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from src.database.base import crear_tablas

from src.routers import auth_router
from src.exceptions.exception_handlers import registrar_error_handlers


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from src.entities.usuario import Usuario
    from src.entities.au import Au
    from src.entities.ficha_personaje import FichaPersonaje

    crear_tablas()
    yield


app: FastAPI = FastAPI(title="Coche Biblioteca", version="1.0.0")


registrar_error_handlers(app=app)

app.include_router(router=auth_router.auth_router)

from datetime import datetime, timezone, timedelta
import os
from typing import Any
from uuid import UUID
from dotenv import load_dotenv
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.exceptions.excepciones import ErrorNoAutorizadoJWT

load_dotenv()

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="auth/login")

KEY: str = os.getenv("JWT_KEY", "")
ALGORITHM: str = os.getenv("ALGORITHM", "")
TOKEN_EXPIRE_MIN: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def crear_token(data: dict[str, Any]):
    payload = data.copy()
    expira = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MIN)
    payload.update({"exp": expira})

    return jwt.encode(payload=payload, key=KEY, algorithm=ALGORITHM)


def verificar_token(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    try:
        payload: dict[str, Any] = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ErrorNoAutorizadoJWT(
            mensaje="Error: El token de acceso expiró. Vuelve a iniciar sesión.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise ErrorNoAutorizadoJWT(
            mensaje="Error: Credenciales inválidas o token modificado externamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verificar_admin(payload: dict[str, Any] = Depends(verificar_token)):
    if not isinstance(payload, dict):
        raise ErrorNoAutorizadoJWT(mensaje="Error interno con el payload.")
    es_admin = payload.get("es_admin")

    if not es_admin:
        raise ErrorNoAutorizadoJWT()
    return payload


def get_id_usuario(payload: dict[str, Any]) -> UUID:
    id_payload: str | None = payload.get("sub")
    if not id_payload:
        raise ErrorNoAutorizadoJWT()
    id_usuario: UUID = UUID(id_payload)

    return id_usuario

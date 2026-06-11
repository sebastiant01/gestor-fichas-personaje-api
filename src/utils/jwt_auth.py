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
ACCESS_TOKEN_EXPIRE_MIN: int = int(os.getenv("ACCESS_TOKEN_EXPIRE", 0))
REFRESH_TOKEN_EXPIRE_DAY: int = int(os.getenv("REFRESH_TOKEN_EXPIRE", 0))


def crear_token(data: dict[str, Any], tipo_token: str):
    payload = data.copy()
    expira = datetime.now(timezone.utc)
    if tipo_token == "access":
        expira += timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    else:
        expira += timedelta(days=REFRESH_TOKEN_EXPIRE_DAY)

    payload.update({"exp": expira})

    return jwt.encode(payload=payload, key=KEY, algorithm=ALGORITHM)


def _decodificar_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ErrorNoAutorizadoJWT(
            mensaje="Error: El token expiró. Vuelve a iniciar sesión.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise ErrorNoAutorizadoJWT(
            mensaje="Error: Token inválido o modificado externamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verificar_token(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    return _decodificar_token(token)


def renovar_token(token: str):
    payload = _decodificar_token(token=token)
    return crear_token(
        data={
            "sub": payload.get("sub"),
            "nombre_usuario": payload.get("nombre_usuario"),
            "es_admin": payload.get("es_admin"),
        },
        tipo_token="access",
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


def _extraer_data_payload(token: str) -> dict:
    payload = _decodificar_token(token)
    return {
        "sub": payload.get("sub"),
        "nombre_usuario": payload.get("nombre_usuario"),
        "es_admin": payload.get("es_admin"),
    }

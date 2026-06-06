import os
from typing import Any, Dict
from dotenv import load_dotenv
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="auth/login")

KEY: str = os.getenv("JWT_KEY") or "secret_key"
ALGORITHM: str = os.getenv("ALGORITHM") or "HS256"


def verify_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    try:
        payload: Dict[str, Any] = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de acceso expiró. Vuelve a iniciar sesión.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas o token modificado externamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_admin(payload: dict = Depends(verify_token)):
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno con el payload.",
        )
    is_admin = payload.get("role")

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido.",
        )
    return payload

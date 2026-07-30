"""
Esquemas Pydantic para autenticación (tokens JWT).
"""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Respuesta de login o refresh con par access/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenResponse(BaseModel):
    """Cuerpo del endpoint ``POST /auth/refresh``."""

    refresh_token: str

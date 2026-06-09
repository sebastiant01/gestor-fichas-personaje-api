from pydantic import BaseModel, Field


class UsuarioLogin(BaseModel):
    nombre_usuario: str = Field(..., min_length=1, max_length=40)
    contrasena: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

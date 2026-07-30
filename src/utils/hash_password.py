"""Hash y verificación de contraseñas con Argon2."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph: PasswordHasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Devuelve el hash Argon2 de ``password``."""
    return ph.hash(password=password)


def verify_password(hashed_password: str, password: str) -> bool:
    """Comprueba la contraseña contra el hash; ``False`` si no coincide."""
    try:
        return ph.verify(hash=hashed_password, password=password)
    except VerifyMismatchError:
        return False

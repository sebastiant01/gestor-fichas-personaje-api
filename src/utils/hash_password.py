from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph: PasswordHasher = PasswordHasher()


def hash_password(password: str) -> str:
    return ph.hash(password=password)


def verify_password(hashed_password: str, password: str) -> bool:
    try:
        return ph.verify(hash=hashed_password, password=password)
    except VerifyMismatchError:
        return False

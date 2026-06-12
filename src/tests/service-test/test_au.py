import uuid
import pytest
from sqlalchemy.orm import Session

from src.services import au_service, usuario_service
from src.exceptions.excepciones import (
    ErrorDatosInvalidos,
    ErrorNoEncontrado,
    AppException,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def usuario_base(db: Session):
    return usuario_service.crear_usuario(
        db=db, nombre_usuario="coche", contrasena="coche123"
    )


@pytest.fixture
def au_base(db: Session, usuario_base):
    return au_service.crear_au(
        db=db, id_usuario=usuario_base.id_usuario, nombre_au="cat"
    )


# ── crear_au ──────────────────────────────────────────────────────────────────


def test_crear_au_exitoso(db: Session, usuario_base):
    au = au_service.crear_au(db=db, id_usuario=usuario_base.id_usuario, nombre_au="cat")
    assert au.nombre_au == "cat"
    assert au.id_usuario == usuario_base.id_usuario


def test_crear_au_nombre_vacio(db: Session, usuario_base):
    with pytest.raises(ErrorDatosInvalidos):
        au_service.crear_au(db=db, id_usuario=usuario_base.id_usuario, nombre_au="")


def test_crear_au_duplicado(db: Session, usuario_base, au_base):
    with pytest.raises(AppException):
        au_service.crear_au(db=db, id_usuario=usuario_base.id_usuario, nombre_au="cat")


def test_crear_au_mismo_nombre_distinto_usuario(db: Session, usuario_base, au_base):
    otro = usuario_service.crear_usuario(
        db=db, nombre_usuario="otra", contrasena="otra1234"
    )
    au = au_service.crear_au(db=db, id_usuario=otro.id_usuario, nombre_au="cat")
    assert au.nombre_au == "cat"


# ── obtener_au ────────────────────────────────────────────────────────────────


def test_obtener_au_por_id_exitoso(db: Session, usuario_base, au_base):
    resultado = au_service.obtener_au_por_id(
        db=db, id_au=au_base.id_au, id_usuario=usuario_base.id_usuario
    )
    assert resultado.id_au == au_base.id_au


def test_obtener_au_por_id_inexistente(db: Session, usuario_base):
    with pytest.raises(ErrorNoEncontrado):
        au_service.obtener_au_por_id(
            db=db, id_au=uuid.uuid4(), id_usuario=usuario_base.id_usuario
        )


def test_obtener_au_por_id_usuario_incorrecto(db: Session, au_base):
    with pytest.raises(AppException):
        au_service.obtener_au_por_id(
            db=db, id_au=au_base.id_au, id_usuario=uuid.uuid4()
        )


def test_obtener_au_por_nombre_exitoso(db: Session, usuario_base, au_base):
    resultado = au_service.obtener_au_por_nombre(
        db=db, id_usuario=usuario_base.id_usuario, nombre_au="cat"
    )
    assert resultado.nombre_au == "cat"  # type: ignore


def test_obtener_au_por_nombre_inexistente(db: Session, usuario_base):
    with pytest.raises(ErrorNoEncontrado):
        au_service.obtener_au_por_nombre(
            db=db, id_usuario=usuario_base.id_usuario, nombre_au="fantasma"
        )


# ── actualizar_au ─────────────────────────────────────────────────────────────


def test_actualizar_au_nombre(db: Session, usuario_base, au_base):
    resultado = au_service.actualizar_au(
        db=db, id_au=au_base.id_au, id_usuario=usuario_base.id_usuario, nombre_au="yyxy"
    )
    assert resultado.nombre_au == "yyxy"


def test_actualizar_au_nombre_duplicado(db: Session, usuario_base, au_base):
    au_service.crear_au(db=db, id_usuario=usuario_base.id_usuario, nombre_au="yyxy")
    with pytest.raises(AppException):
        au_service.actualizar_au(
            db=db,
            id_au=au_base.id_au,
            id_usuario=usuario_base.id_usuario,
            nombre_au="yyxy",
        )


def test_actualizar_au_sin_datos(db: Session, usuario_base, au_base):
    with pytest.raises(ErrorDatosInvalidos):
        au_service.actualizar_au(
            db=db, id_au=au_base.id_au, id_usuario=usuario_base.id_usuario
        )


def test_actualizar_au_usuario_incorrecto(db: Session, au_base):
    with pytest.raises(AppException):
        au_service.actualizar_au(
            db=db, id_au=au_base.id_au, id_usuario=uuid.uuid4(), nombre_au="yyxy"
        )


# ── eliminar_au ───────────────────────────────────────────────────────────────


def test_eliminar_au_exitoso(db: Session, usuario_base, au_base):
    au_service.eliminar_au(
        db=db, id_au=au_base.id_au, id_usuario=usuario_base.id_usuario
    )
    with pytest.raises(ErrorNoEncontrado):
        au_service.obtener_au_por_id(
            db=db, id_au=au_base.id_au, id_usuario=usuario_base.id_usuario
        )


def test_eliminar_au_usuario_incorrecto(db: Session, au_base):
    with pytest.raises(AppException):
        au_service.eliminar_au(db=db, id_au=au_base.id_au, id_usuario=uuid.uuid4())

import pytest
from sqlalchemy.orm import Session

from src.services import usuario_service
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


# ── crear_usuario ─────────────────────────────────────────────────────────────


def test_crear_usuario_exitoso(db: Session):
    usuario = usuario_service.crear_usuario(
        db=db, nombre_usuario="coche", contrasena="coche123"
    )
    assert usuario.nombre_usuario == "coche"
    assert usuario.contrasena_hash != "coche123"


def test_crear_usuario_contrasena_corta(db: Session):
    with pytest.raises(ErrorDatosInvalidos):
        usuario_service.crear_usuario(db=db, nombre_usuario="coche", contrasena="abc")


def test_crear_usuario_contrasena_no_alfanumerica(db: Session):
    with pytest.raises(ErrorDatosInvalidos):
        usuario_service.crear_usuario(
            db=db, nombre_usuario="coche", contrasena="coche!!!"
        )


def test_crear_usuario_duplicado(db: Session, usuario_base):
    with pytest.raises(AppException):
        usuario_service.crear_usuario(
            db=db, nombre_usuario="coche", contrasena="coche123"
        )


def test_crear_usuario_nombre_vacio(db: Session):
    with pytest.raises(ErrorDatosInvalidos):
        usuario_service.crear_usuario(db=db, nombre_usuario="", contrasena="coche123")


# ── obtener_usuario_por_id ────────────────────────────────────────────────────


def test_obtener_usuario_por_id_exitoso(db: Session, usuario_base):
    resultado = usuario_service.obtener_usuario_por_id(
        db=db, id_usuario=usuario_base.id_usuario
    )
    assert resultado.id_usuario == usuario_base.id_usuario  # type: ignore


def test_obtener_usuario_por_id_inexistente(db: Session):
    import uuid

    with pytest.raises(ErrorNoEncontrado):
        usuario_service.obtener_usuario_por_id(db=db, id_usuario=uuid.uuid4())


# ── obtener_usuario_por_nombre ────────────────────────────────────────────────


def test_obtener_usuario_por_nombre_exitoso(db: Session, usuario_base):
    resultado = usuario_service.obtener_usuario_por_nombre_usuario(
        db=db, nombre_usuario="coche"
    )
    assert resultado.nombre_usuario == "coche"


def test_obtener_usuario_por_nombre_inexistente(db: Session):
    with pytest.raises(ErrorNoEncontrado):
        usuario_service.obtener_usuario_por_nombre_usuario(
            db=db, nombre_usuario="fantasma"
        )


def test_obtener_usuario_por_nombre_vacio(db: Session):
    with pytest.raises(ErrorDatosInvalidos):
        usuario_service.obtener_usuario_por_nombre_usuario(db=db, nombre_usuario="")


# ── actualizar_usuario ────────────────────────────────────────────────────────


def test_actualizar_usuario_nombre(db: Session, usuario_base):
    resultado = usuario_service.actualizar_usuario(
        db=db, id_usuario=usuario_base.id_usuario, nombre_usuario="coche_v2"
    )
    assert resultado.nombre_usuario == "coche_v2"


def test_actualizar_usuario_contrasena_se_hashea(db: Session, usuario_base):
    resultado = usuario_service.actualizar_usuario(
        db=db, id_usuario=usuario_base.id_usuario, contrasena="nueva123"
    )
    assert resultado.contrasena_hash != "nueva123"


def test_actualizar_usuario_sin_datos(db: Session, usuario_base):
    with pytest.raises(ErrorDatosInvalidos):
        usuario_service.actualizar_usuario(db=db, id_usuario=usuario_base.id_usuario)


def test_actualizar_usuario_inexistente(db: Session):
    import uuid

    with pytest.raises(ErrorNoEncontrado):
        usuario_service.actualizar_usuario(
            db=db, id_usuario=uuid.uuid4(), nombre_usuario="coche"
        )


# ── eliminar_usuario ──────────────────────────────────────────────────────────


def test_eliminar_usuario_exitoso(db: Session, usuario_base):
    usuario_service.eliminar_usuario(db=db, id_usuario=usuario_base.id_usuario)
    with pytest.raises(ErrorNoEncontrado):
        usuario_service.obtener_usuario_por_id(
            db=db, id_usuario=usuario_base.id_usuario
        )


def test_eliminar_usuario_inexistente(db: Session):
    import uuid

    with pytest.raises(ErrorNoEncontrado):
        usuario_service.eliminar_usuario(db=db, id_usuario=uuid.uuid4())

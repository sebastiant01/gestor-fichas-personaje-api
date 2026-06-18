import uuid
from datetime import date
import pytest
from sqlalchemy.orm import Session

from src.services import ficha_personaje_service, usuario_service, au_service
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


@pytest.fixture
def au_idols(db: Session, usuario_base):
    return au_service.crear_au(
        db=db, id_usuario=usuario_base.id_usuario, nombre_au="idols"
    )


@pytest.fixture
def ficha_base(db: Session, usuario_base, au_base):
    return ficha_personaje_service.crear_ficha_personaje(
        db=db,
        id_usuario=usuario_base.id_usuario,
        id_au=au_base.id_au,
        nombre_personaje="Sakura",
        sexo="Femenino",
        fecha_cumpleanos=date(2000, 4, 1),
    )


# ── crear_ficha ───────────────────────────────────────────────────────────────


def test_crear_ficha_exitoso(db: Session, usuario_base, au_base):
    ficha = ficha_personaje_service.crear_ficha_personaje(
        db=db,
        id_usuario=usuario_base.id_usuario,
        id_au=au_base.id_au,
        nombre_personaje="Sakura",
        sexo="Femenino",
        fecha_cumpleanos=date(2000, 4, 1),
    )
    assert ficha.nombre_personaje == "Sakura"
    assert ficha.edad is None


def test_crear_ficha_con_edad_en_idols(db: Session, usuario_base, au_idols):
    ficha = ficha_personaje_service.crear_ficha_personaje(
        db=db,
        id_usuario=usuario_base.id_usuario,
        id_au=au_idols.id_au,
        nombre_personaje="Hoshi",
        sexo="Masculino",
        fecha_cumpleanos=date(1996, 6, 15),
        edad=28,
    )
    assert ficha.edad == 28


def test_crear_ficha_edad_en_au_no_idols(db: Session, usuario_base, au_base):
    with pytest.raises(ErrorDatosInvalidos):
        ficha_personaje_service.crear_ficha_personaje(
            db=db,
            id_usuario=usuario_base.id_usuario,
            id_au=au_base.id_au,
            nombre_personaje="Sakura",
            sexo="Femenino",
            fecha_cumpleanos=date(2000, 4, 1),
            edad=20,
        )


def test_crear_ficha_edad_negativa_en_idols(db: Session, usuario_base, au_idols):
    with pytest.raises(ErrorDatosInvalidos):
        ficha_personaje_service.crear_ficha_personaje(
            db=db,
            id_usuario=usuario_base.id_usuario,
            id_au=au_idols.id_au,
            nombre_personaje="Hoshi",
            sexo="Masculino",
            fecha_cumpleanos=date(1996, 6, 15),
            edad=-1,
        )


def test_crear_ficha_au_inexistente(db: Session, usuario_base):
    with pytest.raises(ErrorNoEncontrado):
        ficha_personaje_service.crear_ficha_personaje(
            db=db,
            id_usuario=usuario_base.id_usuario,
            id_au=uuid.uuid4(),
            nombre_personaje="Sakura",
            sexo="Femenino",
            fecha_cumpleanos=date(2000, 4, 1),
        )


def test_crear_ficha_nombre_vacio(db: Session, usuario_base, au_base):
    with pytest.raises(ErrorDatosInvalidos):
        ficha_personaje_service.crear_ficha_personaje(
            db=db,
            id_usuario=usuario_base.id_usuario,
            id_au=au_base.id_au,
            nombre_personaje="",
            sexo="Femenino",
            fecha_cumpleanos=date(2000, 4, 1),
        )


# ── obtener_ficha ─────────────────────────────────────────────────────────────


def test_obtener_ficha_por_id_exitoso(db: Session, usuario_base, ficha_base):
    resultado = ficha_personaje_service.obtener_ficha_por_id(
        db=db,
        id_ficha=ficha_base.id_ficha_personaje,
        id_usuario=usuario_base.id_usuario,
    )
    assert resultado.id_ficha_personaje == ficha_base.id_ficha_personaje


def test_obtener_ficha_por_id_inexistente(db: Session, usuario_base):
    with pytest.raises(ErrorNoEncontrado):
        ficha_personaje_service.obtener_ficha_por_id(
            db=db, id_ficha=uuid.uuid4(), id_usuario=usuario_base.id_usuario
        )


def test_obtener_ficha_usuario_incorrecto(db: Session, ficha_base):
    with pytest.raises(AppException):
        ficha_personaje_service.obtener_ficha_por_id(
            db=db, id_ficha=ficha_base.id_ficha_personaje, id_usuario=uuid.uuid4()
        )


def test_obtener_fichas_por_au_exitoso(db: Session, usuario_base, au_base, ficha_base):
    resultado = ficha_personaje_service.obtener_fichas_por_au(
        db=db, id_usuario=usuario_base.id_usuario, id_au=au_base.id_au
    )

    assert isinstance(resultado, list)
    assert len(resultado) == 1
    assert resultado[0].id_au == au_base.id_au


def test_obtener_fichas_por_au_inexistente(db: Session, usuario_base):
    with pytest.raises(ErrorNoEncontrado):
        ficha_personaje_service.obtener_fichas_por_au(
            db=db, id_usuario=usuario_base.id_usuario, id_au=uuid.uuid4()
        )


# ── actualizar_ficha ──────────────────────────────────────────────────────────


def test_actualizar_ficha_nombre(db: Session, usuario_base, ficha_base):
    resultado = ficha_personaje_service.actualizar_ficha(
        db=db,
        id_ficha=ficha_base.id_ficha_personaje,
        id_usuario=usuario_base.id_usuario,
        nombre_personaje="Sakura 🌸",
    )
    assert resultado.nombre_personaje == "Sakura 🌸"


def test_actualizar_ficha_edad_en_au_no_idols(db: Session, usuario_base, ficha_base):
    with pytest.raises(ErrorDatosInvalidos):
        ficha_personaje_service.actualizar_ficha(
            db=db,
            id_ficha=ficha_base.id_ficha_personaje,
            id_usuario=usuario_base.id_usuario,
            edad=20,
        )


def test_actualizar_ficha_sin_datos(db: Session, usuario_base, ficha_base):
    with pytest.raises(ErrorDatosInvalidos):
        ficha_personaje_service.actualizar_ficha(
            db=db,
            id_ficha=ficha_base.id_ficha_personaje,
            id_usuario=usuario_base.id_usuario,
        )


def test_actualizar_ficha_usuario_incorrecto(db: Session, ficha_base):
    with pytest.raises(AppException):
        ficha_personaje_service.actualizar_ficha(
            db=db,
            id_ficha=ficha_base.id_ficha_personaje,
            id_usuario=uuid.uuid4(),
            nombre_personaje="Otra",
        )


# ── eliminar_ficha ────────────────────────────────────────────────────────────


def test_eliminar_ficha_exitoso(db: Session, usuario_base, ficha_base):
    ficha_personaje_service.eliminar_ficha(
        db=db,
        id_ficha=ficha_base.id_ficha_personaje,
        id_usuario=usuario_base.id_usuario,
    )
    with pytest.raises(ErrorNoEncontrado):
        ficha_personaje_service.obtener_ficha_por_id(
            db=db,
            id_ficha=ficha_base.id_ficha_personaje,
            id_usuario=usuario_base.id_usuario,
        )


def test_eliminar_ficha_usuario_incorrecto(db: Session, ficha_base):
    with pytest.raises(AppException):
        ficha_personaje_service.eliminar_ficha(
            db=db, id_ficha=ficha_base.id_ficha_personaje, id_usuario=uuid.uuid4()
        )

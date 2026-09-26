"""Tests unitarios del repositorio ``au_repository``."""

import uuid
import pytest
from sqlalchemy.orm import Session

from src.entities.usuario import Usuario
from src.entities.au import Au
from src.repositories import usuario_repository, au_repository

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def usuario_base(db: Session) -> Usuario:
    usuario = Usuario(
        nombre_usuario="coche",
        contrasena_hash="hash_falso",
        es_admin=True,
    )
    return usuario_repository.crear_usuario(db=db, usuario=usuario)


@pytest.fixture
def au_base(db: Session, usuario_base: Usuario) -> Au:
    au = Au(
        id_usuario=usuario_base.id_usuario,
        nombre_au="cat",
        descripcion_au="AU de gatos",
    )
    return au_repository.crear_au(db=db, au=au)


# ── crear_au ──────────────────────────────────────────────────────────────────


def test_crear_au_retorna_au(db: Session, usuario_base: Usuario):
    au = Au(id_usuario=usuario_base.id_usuario, nombre_au="cat")
    resultado = au_repository.crear_au(db=db, au=au)

    assert resultado.id_au is not None
    assert resultado.nombre_au == "cat"
    assert resultado.id_usuario == usuario_base.id_usuario


def test_crear_au_sin_descripcion(db: Session, usuario_base: Usuario):
    au = Au(id_usuario=usuario_base.id_usuario, nombre_au="yyxy")
    resultado = au_repository.crear_au(db=db, au=au)

    assert resultado.descripcion_au is None


def test_crear_au_nombre_duplicado_mismo_usuario_lanza_error(
    db: Session, usuario_base: Usuario, au_base: Au
):
    au_duplicado = Au(id_usuario=usuario_base.id_usuario, nombre_au="cat")

    with pytest.raises(Exception):
        au_repository.crear_au(db=db, au=au_duplicado)


def test_crear_au_nombre_duplicado_distinto_usuario_es_valido(
    db: Session, usuario_base: Usuario, au_base: Au
):
    otro_usuario = Usuario(
        nombre_usuario="otra", contrasena_hash="hash", es_admin=False
    )
    otro_usuario = usuario_repository.crear_usuario(db=db, usuario=otro_usuario)

    au = Au(id_usuario=otro_usuario.id_usuario, nombre_au="cat")
    resultado = au_repository.crear_au(db=db, au=au)

    assert resultado.id_au is not None


# ── obtener_au_por_id ─────────────────────────────────────────────────────────


def test_obtener_au_por_id_existente(db: Session, au_base: Au):
    resultado = au_repository.obtener_au_por_id(db=db, id_au=au_base.id_au)

    assert resultado is not None
    assert resultado.id_au == au_base.id_au


def test_obtener_au_por_id_inexistente_retorna_none(db: Session):
    resultado = au_repository.obtener_au_por_id(db=db, id_au=uuid.uuid4())

    assert resultado is None


# ── obtener_aus_por_id_usuario ────────────────────────────────────────────────


def test_obtener_aus_por_usuario_retorna_lista(
    db: Session, usuario_base: Usuario, au_base: Au
):
    resultado = au_repository.obtener_aus_por_id_usuario(
        db=db, id_usuario=usuario_base.id_usuario, skip=0, limit=100
    )

    assert isinstance(resultado, list)
    assert len(resultado) == 1


def test_obtener_aus_por_usuario_retorna_todos(db: Session, usuario_base: Usuario):
    for nombre in ["cat", "yyxy", "idols"]:
        au_repository.crear_au(
            db=db, au=Au(id_usuario=usuario_base.id_usuario, nombre_au=nombre)
        )

    resultado = au_repository.obtener_aus_por_id_usuario(
        db=db, id_usuario=usuario_base.id_usuario, skip=0, limit=100
    )

    assert len(resultado) == 3


def test_obtener_aus_por_usuario_sin_aus_retorna_lista_vacia(
    db: Session, usuario_base: Usuario
):
    resultado = au_repository.obtener_aus_por_id_usuario(
        db=db, id_usuario=usuario_base.id_usuario, skip=0, limit=100
    )

    assert resultado == []


# ── obtener_au_por_nombre ─────────────────────────────────────────────────────


def test_obtener_au_por_nombre_existente(
    db: Session, usuario_base: Usuario, au_base: Au
):
    resultado = au_repository.obtener_au_por_nombre(
        db=db, id_usuario=usuario_base.id_usuario, nombre_au="cat"
    )

    assert resultado is not None
    assert resultado.nombre_au == "cat"


def test_obtener_au_por_nombre_inexistente_retorna_none(
    db: Session, usuario_base: Usuario
):
    resultado = au_repository.obtener_au_por_nombre(
        db=db, id_usuario=usuario_base.id_usuario, nombre_au="fantasma"
    )

    assert resultado is None


# ── actualizar_au ─────────────────────────────────────────────────────────────


def test_actualizar_au_nombre(db: Session, au_base: Au):
    resultado = au_repository.actualizar_au(
        db=db, au=au_base, datos={"nombre_au": "idols"}
    )

    assert resultado.nombre_au == "idols"


def test_actualizar_au_descripcion(db: Session, au_base: Au):
    resultado = au_repository.actualizar_au(
        db=db, au=au_base, datos={"descripcion_au": "Nueva descripción"}
    )

    assert resultado.descripcion_au == "Nueva descripción"


def test_actualizar_au_persiste_en_db(db: Session, au_base: Au):
    au_repository.actualizar_au(db=db, au=au_base, datos={"nombre_au": "yyxy"})
    consultado = au_repository.obtener_au_por_id(db=db, id_au=au_base.id_au)

    assert consultado.nombre_au == "yyxy"  # type: ignore


# ── eliminar_au ───────────────────────────────────────────────────────────────


def test_eliminar_au_lo_borra_de_db(db: Session, au_base: Au):
    au_repository.eliminar_au(db=db, au=au_base)
    resultado = au_repository.obtener_au_por_id(db=db, id_au=au_base.id_au)

    assert resultado is None


def test_eliminar_au_reduce_conteo(db: Session, usuario_base: Usuario, au_base: Au):
    antes = au_repository.obtener_aus_por_id_usuario(
        db=db, id_usuario=usuario_base.id_usuario, skip=0, limit=100
    )
    assert len(antes) == 1

    au_repository.eliminar_au(db=db, au=au_base)

    despues = au_repository.obtener_aus_por_id_usuario(
        db=db, id_usuario=usuario_base.id_usuario, skip=0, limit=100
    )
    assert len(despues) == 0

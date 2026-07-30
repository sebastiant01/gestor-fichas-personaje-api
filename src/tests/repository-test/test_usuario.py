"""Tests unitarios del repositorio ``usuario_repository``."""

import uuid
import pytest
from sqlalchemy.orm import Session

from src.entities.usuario import Usuario
from src.repositories import usuario_repository

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def usuario_base(db: Session) -> Usuario:
    """Crea y persiste un usuario base reutilizable en cada test."""
    usuario = Usuario(
        nombre_usuario="coche",
        contrasena_hash="hash_falso_para_tests",
        es_admin=True,
    )
    return usuario_repository.crear_usuario(db=db, usuario=usuario)


# ── crear_usuario ─────────────────────────────────────────────────────────────


def test_crear_usuario_retorna_usuario(db: Session):
    usuario = Usuario(
        nombre_usuario="coche",
        contrasena_hash="hash_falso",
        es_admin=True,
    )
    resultado = usuario_repository.crear_usuario(db=db, usuario=usuario)

    assert resultado.id_usuario is not None
    assert resultado.nombre_usuario == "coche"
    assert resultado.contrasena_hash == "hash_falso"
    assert resultado.es_admin is True


def test_crear_usuario_genera_id_unico(db: Session):
    u1 = Usuario(nombre_usuario="coche", contrasena_hash="hash1", es_admin=True)
    u2 = Usuario(nombre_usuario="otra", contrasena_hash="hash2", es_admin=False)

    r1 = usuario_repository.crear_usuario(db=db, usuario=u1)
    r2 = usuario_repository.crear_usuario(db=db, usuario=u2)

    assert r1.id_usuario != r2.id_usuario


def test_crear_usuario_nombre_duplicado_lanza_error(db: Session):
    u1 = Usuario(nombre_usuario="coche", contrasena_hash="hash1", es_admin=True)
    u2 = Usuario(nombre_usuario="coche", contrasena_hash="hash2", es_admin=False)

    usuario_repository.crear_usuario(db=db, usuario=u1)

    with pytest.raises(Exception):
        usuario_repository.crear_usuario(db=db, usuario=u2)


# ── obtener_usuario_por_id ────────────────────────────────────────────────────


def test_obtener_usuario_por_id_existente(db: Session, usuario_base: Usuario):
    resultado = usuario_repository.obtener_usuario_por_id(
        db=db, id_usuario=usuario_base.id_usuario
    )

    assert resultado is not None
    assert resultado.id_usuario == usuario_base.id_usuario
    assert resultado.nombre_usuario == "coche"


def test_obtener_usuario_por_id_inexistente_retorna_none(db: Session):
    resultado = usuario_repository.obtener_usuario_por_id(
        db=db, id_usuario=uuid.uuid4()
    )

    assert resultado is None


# ── obtener_usuario_por_nombre_usuario ────────────────────────────────────────


def test_obtener_usuario_por_nombre_existente(db: Session, usuario_base: Usuario):
    resultado = usuario_repository.obtener_usuario_por_nombre_usuario(
        db=db, nombre_usuario="coche"
    )

    assert resultado is not None
    assert resultado.nombre_usuario == "coche"


def test_obtener_usuario_por_nombre_inexistente_retorna_none(db: Session):
    resultado = usuario_repository.obtener_usuario_por_nombre_usuario(
        db=db, nombre_usuario="fantasma"
    )

    assert resultado is None


def test_obtener_usuario_por_nombre_case_sensitive(db: Session, usuario_base: Usuario):
    resultado = usuario_repository.obtener_usuario_por_nombre_usuario(
        db=db, nombre_usuario="COCHE"
    )

    assert resultado is None


# ── obtener_usuarios ──────────────────────────────────────────────────────────


def test_obtener_usuarios_retorna_lista(db: Session, usuario_base: Usuario):
    resultado = usuario_repository.obtener_usuarios(db=db, skip=0, limit=100)

    assert isinstance(resultado, list)
    assert len(resultado) == 1


def test_obtener_usuarios_skip_y_limit(db: Session):
    for i in range(5):
        u = Usuario(
            nombre_usuario=f"usuario_{i}", contrasena_hash="hash", es_admin=False
        )
        usuario_repository.crear_usuario(db=db, usuario=u)

    resultado = usuario_repository.obtener_usuarios(db=db, skip=2, limit=2)

    assert len(resultado) == 2


def test_obtener_usuarios_lista_vacia(db: Session):
    resultado = usuario_repository.obtener_usuarios(db=db, skip=0, limit=100)

    assert resultado == []


# ── actualizar_usuario ────────────────────────────────────────────────────────


def test_actualizar_usuario_nombre(db: Session, usuario_base: Usuario):
    resultado = usuario_repository.actualizar_usuario(
        db=db,
        usuario=usuario_base,
        datos={"nombre_usuario": "coche_actualizada"},
    )

    assert resultado.nombre_usuario == "coche_actualizada"


def test_actualizar_usuario_es_admin(db: Session, usuario_base: Usuario):
    resultado = usuario_repository.actualizar_usuario(
        db=db,
        usuario=usuario_base,
        datos={"es_admin": False},
    )

    assert resultado.es_admin is False


def test_actualizar_usuario_multiples_campos(db: Session, usuario_base: Usuario):
    resultado = usuario_repository.actualizar_usuario(
        db=db,
        usuario=usuario_base,
        datos={"nombre_usuario": "nuevo_nombre", "contrasena_hash": "nuevo_hash"},
    )

    assert resultado.nombre_usuario == "nuevo_nombre"
    assert resultado.contrasena_hash == "nuevo_hash"


def test_actualizar_usuario_persiste_en_db(db: Session, usuario_base: Usuario):
    usuario_repository.actualizar_usuario(
        db=db,
        usuario=usuario_base,
        datos={"nombre_usuario": "coche_v2"},
    )
    consultado = usuario_repository.obtener_usuario_por_id(
        db=db, id_usuario=usuario_base.id_usuario
    )

    assert consultado.nombre_usuario == "coche_v2"  # type: ignore


# ── eliminar_usuario ──────────────────────────────────────────────────────────


def test_eliminar_usuario_lo_borra_de_db(db: Session, usuario_base: Usuario):
    usuario_repository.eliminar_usuario(db=db, usuario=usuario_base)

    resultado = usuario_repository.obtener_usuario_por_id(
        db=db, id_usuario=usuario_base.id_usuario
    )
    assert resultado is None


def test_eliminar_usuario_reduce_conteo(db: Session, usuario_base: Usuario):
    antes = usuario_repository.obtener_usuarios(db=db, skip=0, limit=100)
    assert len(antes) == 1

    usuario_repository.eliminar_usuario(db=db, usuario=usuario_base)

    despues = usuario_repository.obtener_usuarios(db=db, skip=0, limit=100)
    assert len(despues) == 0

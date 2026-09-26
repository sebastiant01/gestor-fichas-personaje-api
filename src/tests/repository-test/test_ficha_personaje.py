# tests/repositories/test_ficha_personaje_repository.py
"""Tests unitarios del repositorio ``ficha_personaje_repository``."""

import uuid
from datetime import date
import pytest
from sqlalchemy.orm import Session

from src.entities.usuario import Usuario
from src.entities.au import Au
from src.entities.ficha_personaje import FichaPersonaje
from src.repositories import (
    usuario_repository,
    au_repository,
    ficha_personaje_repository,
)

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
    au = Au(id_usuario=usuario_base.id_usuario, nombre_au="cat")
    return au_repository.crear_au(db=db, au=au)


@pytest.fixture
def au_idols(db: Session, usuario_base: Usuario) -> Au:
    au = Au(id_usuario=usuario_base.id_usuario, nombre_au="idols")
    return au_repository.crear_au(db=db, au=au)


@pytest.fixture
def ficha_base(db: Session, usuario_base: Usuario, au_base: Au) -> FichaPersonaje:
    ficha = FichaPersonaje(
        id_usuario=usuario_base.id_usuario,
        id_au=au_base.id_au,
        nombre_personaje="Sakura",
        sexo="Femenino",
        fecha_cumpleanos=date(2000, 4, 1),
        signo_zodiacal="Aries",
    )
    return ficha_personaje_repository.crear_ficha_personaje(db=db, ficha=ficha)


# ── crear_ficha_personaje ─────────────────────────────────────────────────────


def test_crear_ficha_retorna_ficha(db: Session, usuario_base: Usuario, au_base: Au):
    ficha = FichaPersonaje(
        id_usuario=usuario_base.id_usuario,
        id_au=au_base.id_au,
        nombre_personaje="Sakura",
        sexo="Femenino",
        fecha_cumpleanos=date(2000, 4, 1),
    )
    resultado = ficha_personaje_repository.crear_ficha_personaje(db=db, ficha=ficha)

    assert resultado.id_ficha_personaje is not None
    assert resultado.nombre_personaje == "Sakura"
    assert resultado.id_au == au_base.id_au


def test_crear_ficha_campos_opcionales_son_none(
    db: Session, usuario_base: Usuario, au_base: Au
):
    ficha = FichaPersonaje(
        id_usuario=usuario_base.id_usuario,
        id_au=au_base.id_au,
        nombre_personaje="Sakura",
        sexo="Femenino",
        fecha_cumpleanos=date(2000, 4, 1),
    )
    resultado = ficha_personaje_repository.crear_ficha_personaje(db=db, ficha=ficha)

    assert resultado.edad is None
    assert resultado.descripcion_personaje is None
    assert resultado.url_imagen is None
    assert resultado.url_musica is None


def test_crear_ficha_mismo_nombre_distinto_au(
    db: Session, usuario_base: Usuario, au_base: Au, au_idols: Au
):
    ficha1 = FichaPersonaje(
        id_usuario=usuario_base.id_usuario,
        id_au=au_base.id_au,
        nombre_personaje="Sakura",
        sexo="Femenino",
        fecha_cumpleanos=date(2000, 4, 1),
    )
    ficha2 = FichaPersonaje(
        id_usuario=usuario_base.id_usuario,
        id_au=au_idols.id_au,
        nombre_personaje="Sakura",
        sexo="Femenino",
        fecha_cumpleanos=date(2000, 4, 1),
    )
    r1 = ficha_personaje_repository.crear_ficha_personaje(db=db, ficha=ficha1)
    r2 = ficha_personaje_repository.crear_ficha_personaje(db=db, ficha=ficha2)

    assert r1.id_ficha_personaje != r2.id_ficha_personaje


# ── obtener_ficha_por_id ──────────────────────────────────────────────────────


def test_obtener_ficha_por_id_existente(db: Session, ficha_base: FichaPersonaje):
    resultado = ficha_personaje_repository.obtener_ficha_por_id(
        db=db, id_ficha=ficha_base.id_ficha_personaje
    )

    assert resultado is not None
    assert resultado.id_ficha_personaje == ficha_base.id_ficha_personaje


def test_obtener_ficha_por_id_inexistente_retorna_none(db: Session):
    resultado = ficha_personaje_repository.obtener_ficha_por_id(
        db=db, id_ficha=uuid.uuid4()
    )

    assert resultado is None


# ── obtener_fichas_por_id_usuario ─────────────────────────────────────────────


def test_obtener_fichas_por_usuario_retorna_lista(
    db: Session, usuario_base: Usuario, ficha_base: FichaPersonaje
):
    resultado = ficha_personaje_repository.obtener_fichas_por_id_usuario(
        db=db, id_usuario=usuario_base.id_usuario, skip=0, limit=100
    )

    assert isinstance(resultado, list)
    assert len(resultado) == 1


def test_obtener_fichas_por_usuario_sin_fichas_retorna_lista_vacia(
    db: Session, usuario_base: Usuario
):
    resultado = ficha_personaje_repository.obtener_fichas_por_id_usuario(
        db=db, id_usuario=usuario_base.id_usuario, skip=0, limit=100
    )

    assert resultado == []


# ── obtener_fichas_por_au ─────────────────────────────────────────────────────


def test_obtener_fichas_por_au_retorna_fichas(
    db: Session, usuario_base: Usuario, au_base: Au, ficha_base: FichaPersonaje
):
    resultado = ficha_personaje_repository.obtener_fichas_por_au(
        db=db, id_usuario=usuario_base.id_usuario, id_au=au_base.id_au, skip=0, limit=100
    )

    assert isinstance(resultado, list)
    assert len(resultado) == 1
    assert resultado[0].id_au == au_base.id_au


def test_obtener_fichas_por_au_no_mezcla_aus(
    db: Session,
    usuario_base: Usuario,
    au_base: Au,
    au_idols: Au,
    ficha_base: FichaPersonaje,
):
    # ficha_base pertenece a au_base; au_idols no tiene fichas
    resultado = ficha_personaje_repository.obtener_fichas_por_au(
        db=db, id_usuario=usuario_base.id_usuario, id_au=au_idols.id_au, skip=0, limit=100
    )

    assert resultado == []


# ── obtener_fichas_por_nombre_personaje ───────────────────────────────────────


def test_obtener_fichas_por_nombre_existente(
    db: Session, usuario_base: Usuario, ficha_base: FichaPersonaje
):
    resultado = ficha_personaje_repository.obtener_fichas_por_nombre_personaje(
        db=db, id_usuario=usuario_base.id_usuario, nombre_personaje="Sakura", skip=0, limit=100
    )

    assert len(resultado) == 1
    assert resultado[0].nombre_personaje == "Sakura"


def test_obtener_fichas_por_nombre_inexistente_retorna_lista_vacia(
    db: Session, usuario_base: Usuario
):
    resultado = ficha_personaje_repository.obtener_fichas_por_nombre_personaje(
        db=db, id_usuario=usuario_base.id_usuario, nombre_personaje="Fantasma", skip=0, limit=100
    )

    assert resultado == []


# ── obtener_fichas_por_signo ──────────────────────────────────────────────────


def test_obtener_fichas_por_signo_existente(
    db: Session, usuario_base: Usuario, ficha_base: FichaPersonaje
):
    resultado = ficha_personaje_repository.obtener_fichas_por_signo(
        db=db, id_usuario=usuario_base.id_usuario, signo_zodiacal="Aries", skip=0, limit=100
    )

    assert len(resultado) == 1
    assert resultado[0].signo_zodiacal == "Aries"


def test_obtener_fichas_por_signo_inexistente_retorna_lista_vacia(
    db: Session, usuario_base: Usuario
):
    resultado = ficha_personaje_repository.obtener_fichas_por_signo(
        db=db, id_usuario=usuario_base.id_usuario, signo_zodiacal="Escorpio", skip=0, limit=100
    )

    assert resultado == []


# ── obtener_fichas_por_sexo ───────────────────────────────────────────────────


def test_obtener_fichas_por_sexo_existente(
    db: Session, usuario_base: Usuario, ficha_base: FichaPersonaje
):
    resultado = ficha_personaje_repository.obtener_fichas_por_sexo(
        db=db, id_usuario=usuario_base.id_usuario, sexo="Femenino", skip=0, limit=100
    )

    assert len(resultado) == 1
    assert resultado[0].sexo == "Femenino"


def test_obtener_fichas_por_sexo_inexistente_retorna_lista_vacia(
    db: Session, usuario_base: Usuario
):
    resultado = ficha_personaje_repository.obtener_fichas_por_sexo(
        db=db, id_usuario=usuario_base.id_usuario, sexo="Masculino", skip=0, limit=100
    )

    assert resultado == []


# ── obtener_fichas_por_cumpleanos ─────────────────────────────────────────────


def test_obtener_fichas_por_cumpleanos_existente(
    db: Session, usuario_base: Usuario, ficha_base: FichaPersonaje
):
    resultado = ficha_personaje_repository.obtener_fichas_por_cumpleanos(
        db=db, id_usuario=usuario_base.id_usuario, fecha_cumpleanos=date(2000, 4, 1), skip=0, limit=100
    )

    assert len(resultado) == 1


def test_obtener_fichas_por_cumpleanos_inexistente_retorna_lista_vacia(
    db: Session, usuario_base: Usuario
):
    resultado = ficha_personaje_repository.obtener_fichas_por_cumpleanos(
        db=db, id_usuario=usuario_base.id_usuario, fecha_cumpleanos=date(1999, 1, 1), skip=0, limit=100
    )

    assert resultado == []


# ── obtener_fichas_por_dia y mes ──────────────────────────────────────────────


def test_obtener_fichas_por_dia_cumpleanos(
    db: Session, usuario_base: Usuario, ficha_base: FichaPersonaje
):
    resultado = ficha_personaje_repository.obtener_fichas_por_dia_cumpleanos(
        db=db, id_usuario=usuario_base.id_usuario, dia=1, skip=0, limit=100
    )

    assert len(resultado) >= 1


def test_obtener_fichas_por_mes_cumpleanos(
    db: Session, usuario_base: Usuario, ficha_base: FichaPersonaje
):
    resultado = ficha_personaje_repository.obtener_fichas_por_mes_cumpleanos(
        db=db, id_usuario=usuario_base.id_usuario, mes=4, skip=0, limit=100
    )

    assert len(resultado) >= 1


def test_obtener_fichas_por_dia_sin_resultados(
    db: Session, usuario_base: Usuario, ficha_base: FichaPersonaje
):
    resultado = ficha_personaje_repository.obtener_fichas_por_dia_cumpleanos(
        db=db, id_usuario=usuario_base.id_usuario, dia=15, skip=0, limit=100
    )

    assert resultado == []


# ── actualizar_ficha ──────────────────────────────────────────────────────────


def test_actualizar_ficha_nombre(db: Session, ficha_base: FichaPersonaje):
    resultado = ficha_personaje_repository.actualizar_ficha(
        db=db, ficha=ficha_base, datos={"nombre_personaje": "Sakura 🌸"}
    )

    assert resultado.nombre_personaje == "Sakura 🌸"


def test_actualizar_ficha_multiples_campos(db: Session, ficha_base: FichaPersonaje):
    resultado = ficha_personaje_repository.actualizar_ficha(
        db=db,
        ficha=ficha_base,
        datos={
            "nombre_personaje": "Luna",
            "sexo": "No binario",
            "signo_zodiacal": "Libra",
        },
    )

    assert resultado.nombre_personaje == "Luna"
    assert resultado.sexo == "No binario"
    assert resultado.signo_zodiacal == "Libra"


def test_actualizar_ficha_persiste_en_db(db: Session, ficha_base: FichaPersonaje):
    ficha_personaje_repository.actualizar_ficha(
        db=db, ficha=ficha_base, datos={"nombre_personaje": "Hinata"}
    )
    consultada = ficha_personaje_repository.obtener_ficha_por_id(
        db=db, id_ficha=ficha_base.id_ficha_personaje
    )

    assert consultada.nombre_personaje == "Hinata"  # type: ignore


# ── eliminar_ficha ────────────────────────────────────────────────────────────


def test_eliminar_ficha_la_borra_de_db(db: Session, ficha_base: FichaPersonaje):
    ficha_personaje_repository.eliminar_ficha(db=db, ficha=ficha_base)
    resultado = ficha_personaje_repository.obtener_ficha_por_id(
        db=db, id_ficha=ficha_base.id_ficha_personaje
    )

    assert resultado is None


def test_eliminar_ficha_reduce_conteo(
    db: Session, usuario_base: Usuario, ficha_base: FichaPersonaje
):
    antes = ficha_personaje_repository.obtener_fichas_por_id_usuario(
        db=db, id_usuario=usuario_base.id_usuario, skip=0, limit=100
    )
    assert len(antes) == 1

    ficha_personaje_repository.eliminar_ficha(db=db, ficha=ficha_base)

    despues = ficha_personaje_repository.obtener_fichas_por_id_usuario(
        db=db, id_usuario=usuario_base.id_usuario, skip=0, limit=100
    )
    assert len(despues) == 0

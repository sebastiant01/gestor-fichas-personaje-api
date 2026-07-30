"""Reglas de negocio para fichas de personaje.

Valida AU, permisos, regla de ``edad`` en AUs «idols», imágenes de
Cloudinary y cache.
"""

import uuid
import json
from datetime import date

from sqlalchemy.orm import Session

from src.entities.ficha_personaje import FichaPersonaje
from src.entities.au import Au
from src.exceptions.excepciones import (
    AppException,
    ErrorDatosInvalidos,
    ErrorNoEncontrado,
)
from src.repositories import ficha_personaje_repository, au_repository
from src.schemas.ficha_personaje_schema import FichaPersonajeResponse
from src.utils.image_manager import eliminar_imagen, TIPOS_PERMITIDOS, subir_imagen
from src.utils.caching_redis import (
    obtener_respuesta_cache,
    guardar_respuesta_cache,
    invalidar_cache_por_prefijo,
)

from fastapi import status, UploadFile


def _cache_key_fichas_personajes(
    id_usuario: uuid.UUID,
    id_au: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
):
    """Construye la clave Redis para listados de fichas de personaje.

    Args:
        id_usuario: Identificador UUID del usuario propietario.
        id_au: Identificador UUID del AU para filtrar, o ``None`` para
            el listado general del usuario.
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        str: Clave Redis en el formato
        ``fichas:usuario:<id_usuario>:<id_au>:<skip>:<limit>``.
    """
    return f"fichas:usuario:{id_usuario}:{id_au}:{skip}:{limit}"


def crear_ficha_personaje(
    db: Session,
    id_usuario: uuid.UUID,
    id_au: uuid.UUID,
    nombre_personaje: str,
    sexo: str,
    fecha_cumpleanos: date,
    descripcion_personaje: str | None = None,
    edad: int | None = None,
    signo_zodiacal: str | None = None,
    url_imagen: str | None = None,
    url_musica: str | None = None,
) -> FichaPersonaje:
    """Crea una ficha de personaje validando AU, permisos y regla de edad.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        id_au: Identificador UUID del AU al que pertenecerá la ficha.
        nombre_personaje: Nombre del personaje.
        sexo: Sexo del personaje.
        fecha_cumpleanos: Fecha de cumpleaños del personaje.
        descripcion_personaje: Descripción opcional del personaje.
        edad: Edad del personaje; solo permitida si el AU es ``idols``.
        signo_zodiacal: Signo zodiacal opcional.
        url_imagen: URL opcional de la imagen del personaje.
        url_musica: URL opcional de música asociada al personaje.

    Returns:
        FichaPersonaje: Ficha recién creada.

    Raises:
        ErrorDatosInvalidos: Si faltan campos obligatorios, o si
            ``edad`` no es válida para el AU indicado.
        ErrorNoEncontrado: Si el AU indicado no existe.
        AppException: Si el AU no pertenece al usuario (403).
    """
    if not nombre_personaje:
        raise ErrorDatosInvalidos(
            mensaje="Error: Debe ingresar un nombre para el personaje."
        )
    if not sexo:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar el sexo del personaje.")
    if not fecha_cumpleanos:
        raise ErrorDatosInvalidos(
            mensaje="Error: Debe ingresar la fecha de cumpleaños."
        )

    au: Au | None = au_repository.obtener_au_por_id(db=db, id_au=id_au)
    if not au:
        raise ErrorNoEncontrado("AU")
    if au.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para usar este AU.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )

    if edad is not None and "idols" not in au.nombre_au.lower():
        raise ErrorDatosInvalidos(
            mensaje="Error: La edad solo está permitida en el AU 'idols'."
        )
    if "idols" in au.nombre_au.lower() and edad is not None and edad <= 0:
        raise ErrorDatosInvalidos(mensaje="Error: La edad debe ser mayor a 0.")

    nueva_ficha: FichaPersonaje = FichaPersonaje(
        id_usuario=id_usuario,
        id_au=id_au,
        nombre_personaje=nombre_personaje,
        sexo=sexo,
        fecha_cumpleanos=fecha_cumpleanos,
        descripcion_personaje=descripcion_personaje,
        edad=edad,
        signo_zodiacal=signo_zodiacal,
        url_imagen=url_imagen,
        url_musica=url_musica,
    )
    ficha_creada = ficha_personaje_repository.crear_ficha_personaje(
        db=db, ficha=nueva_ficha
    )
    invalidar_cache_por_prefijo(
        f"fichas:usuario:{id_usuario}:None:",
        f"fichas:usuario:{id_usuario}:{id_au}:",
    )
    return ficha_creada


def obtener_fichas_por_usuario(
    db: Session, id_usuario: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[FichaPersonaje] | list[dict]:
    """Lista fichas del usuario, sirviendo desde cache cuando es posible.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        list[FichaPersonaje] | list[dict]: Entidades si la consulta fue
        a base de datos, o una lista de diccionarios si vino de cache.
    """
    cache_key = _cache_key_fichas_personajes(
        id_usuario=id_usuario, skip=skip, limit=limit
    )
    resultado_cache = obtener_respuesta_cache(cache_key=cache_key)
    if resultado_cache:
        return resultado_cache

    fichas = ficha_personaje_repository.obtener_fichas_por_id_usuario(
        db=db, id_usuario=id_usuario, skip=skip, limit=limit
    )
    fichas_json = json.dumps(
        [
            FichaPersonajeResponse.model_validate(f).model_dump(mode="json")
            for f in fichas
        ]
    )
    guardar_respuesta_cache(cache_key=cache_key, valor=fichas_json)
    return fichas


def obtener_ficha_por_id(
    db: Session,
    id_ficha: uuid.UUID,
    id_usuario: uuid.UUID,
) -> FichaPersonaje:
    """Obtiene una ficha de personaje verificando que pertenezca al usuario.

    Args:
        db: Sesión de base de datos.
        id_ficha: Identificador UUID de la ficha.
        id_usuario: Identificador UUID del usuario propietario esperado.

    Returns:
        FichaPersonaje: Ficha solicitada.

    Raises:
        ErrorNoEncontrado: Si la ficha no existe.
        AppException: Si la ficha pertenece a otro usuario (403).
    """
    ficha: FichaPersonaje | None = ficha_personaje_repository.obtener_ficha_por_id(
        db=db, id_ficha=id_ficha
    )
    if not ficha:
        raise ErrorNoEncontrado("Ficha de personaje")
    if ficha.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para acceder a esta ficha.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )
    return ficha


def obtener_fichas_por_au(
    db: Session,
    id_usuario: uuid.UUID,
    id_au: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[FichaPersonaje] | list[dict]:
    """Lista fichas de un AU concreto, sirviendo desde cache cuando es posible.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        id_au: Identificador UUID del AU cuyas fichas se listarán.
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        list[FichaPersonaje] | list[dict]: Entidades si la consulta fue
        a base de datos, o una lista de diccionarios si vino de cache.

    Raises:
        ErrorNoEncontrado: Si el AU no existe.
        AppException: Si el AU no pertenece al usuario (403).
    """
    cache_key = _cache_key_fichas_personajes(
        id_usuario=id_usuario, id_au=id_au, skip=skip, limit=limit
    )
    resultado_cache = obtener_respuesta_cache(cache_key=cache_key)
    if resultado_cache:
        return resultado_cache
    au: Au | None = au_repository.obtener_au_por_id(db=db, id_au=id_au)
    if not au:
        raise ErrorNoEncontrado("AU")
    if au.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para usar este AU.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )

    fichas = ficha_personaje_repository.obtener_fichas_por_au(
        db=db, id_usuario=id_usuario, id_au=id_au, skip=skip, limit=limit
    )
    fichas_json = json.dumps(
        [
            FichaPersonajeResponse.model_validate(f).model_dump(mode="json")
            for f in fichas
        ]
    )
    guardar_respuesta_cache(cache_key=cache_key, valor=fichas_json)
    return fichas


def obtener_fichas_por_nombre_personaje(
    db: Session,
    id_usuario: uuid.UUID,
    nombre_personaje: str,
    skip: int = 0,
    limit: int = 100,
) -> list[FichaPersonaje]:
    """Busca fichas de personaje por nombre exacto.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        nombre_personaje: Nombre de personaje a buscar.
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        list[FichaPersonaje]: Fichas que coinciden con el nombre.

    Raises:
        ErrorDatosInvalidos: Si ``nombre_personaje`` está vacío.
    """
    if not nombre_personaje:
        raise ErrorDatosInvalidos(
            mensaje="Error: Debe ingresar un nombre de personaje."
        )
    return ficha_personaje_repository.obtener_fichas_por_nombre_personaje(
        db=db,
        id_usuario=id_usuario,
        nombre_personaje=nombre_personaje,
        skip=skip,
        limit=limit,
    )


def obtener_fichas_por_signo(
    db: Session,
    id_usuario: uuid.UUID,
    signo_zodiacal: str,
    skip: int = 0,
    limit: int = 100,
) -> list[FichaPersonaje]:
    """Filtra fichas de personaje por signo zodiacal.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        signo_zodiacal: Signo zodiacal a buscar.
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        list[FichaPersonaje]: Fichas que coinciden con el signo.

    Raises:
        ErrorDatosInvalidos: Si ``signo_zodiacal`` está vacío.
    """
    if not signo_zodiacal:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar un signo zodiacal.")
    return ficha_personaje_repository.obtener_fichas_por_signo(
        db=db,
        id_usuario=id_usuario,
        signo_zodiacal=signo_zodiacal,
        skip=skip,
        limit=limit,
    )


def obtener_fichas_por_sexo(
    db: Session, id_usuario: uuid.UUID, sexo: str, skip: int = 0, limit: int = 100
) -> list[FichaPersonaje]:
    """Filtra fichas de personaje por sexo.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        sexo: Valor de sexo a buscar.
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        list[FichaPersonaje]: Fichas que coinciden con el sexo.

    Raises:
        ErrorDatosInvalidos: Si ``sexo`` está vacío.
    """
    if not sexo:
        raise ErrorDatosInvalidos(mensaje="Error: Debe ingresar un sexo.")
    return ficha_personaje_repository.obtener_fichas_por_sexo(
        db=db, id_usuario=id_usuario, sexo=sexo, skip=skip, limit=limit
    )


def obtener_fichas_por_cumpleanos(
    db: Session,
    id_usuario: uuid.UUID,
    fecha_cumpleanos: date,
    skip: int = 0,
    limit: int = 100,
) -> list[FichaPersonaje]:
    """Filtra fichas por una fecha de cumpleaños exacta.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        fecha_cumpleanos: Fecha exacta de cumpleaños a buscar.
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        list[FichaPersonaje]: Fichas con esa fecha de cumpleaños.
    """
    return ficha_personaje_repository.obtener_fichas_por_cumpleanos(
        db=db,
        id_usuario=id_usuario,
        fecha_cumpleanos=fecha_cumpleanos,
        skip=skip,
        limit=limit,
    )


def obtener_fichas_por_dia_cumpleanos(
    db: Session, id_usuario: uuid.UUID, dia: int, skip: int = 0, limit: int = 100
) -> list[FichaPersonaje]:
    """Filtra fichas cuyo cumpleaños cae en un día del mes (1-31).

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        dia: Día del mes a buscar.
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        list[FichaPersonaje]: Fichas cuyo cumpleaños cae en ese día.

    Raises:
        ErrorDatosInvalidos: Si ``dia`` está fuera del rango 1-31.
    """
    if dia < 1 or dia > 31:
        raise ErrorDatosInvalidos(mensaje="Error: El día debe estar entre 1 y 31.")
    return ficha_personaje_repository.obtener_fichas_por_dia_cumpleanos(
        db=db, id_usuario=id_usuario, dia=dia, skip=skip, limit=limit
    )


def obtener_fichas_por_mes_cumpleanos(
    db: Session, id_usuario: uuid.UUID, mes: int, skip: int = 0, limit: int = 100
) -> list[FichaPersonaje]:
    """Filtra fichas cuyo cumpleaños cae en un mes (1-12).

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario.
        mes: Mes a buscar.
        skip: Cantidad de registros a omitir.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        list[FichaPersonaje]: Fichas cuyo cumpleaños cae en ese mes.

    Raises:
        ErrorDatosInvalidos: Si ``mes`` está fuera del rango 1-12.
    """
    if mes < 1 or mes > 12:
        raise ErrorDatosInvalidos(mensaje="Error: El mes debe estar entre 1 y 12.")
    return ficha_personaje_repository.obtener_fichas_por_mes_cumpleanos(
        db=db, id_usuario=id_usuario, mes=mes, skip=skip, limit=limit
    )


def actualizar_ficha(
    db: Session, id_ficha: uuid.UUID, id_usuario: uuid.UUID, **kwargs
) -> FichaPersonaje:
    """Actualiza una ficha propia, validando AU destino y regla de edad.

    Args:
        db: Sesión de base de datos.
        id_ficha: Identificador UUID de la ficha a actualizar.
        id_usuario: Identificador UUID del usuario propietario esperado.
        **kwargs: Campos a actualizar (por ejemplo ``id_au``, ``edad`` o
            ``nombre_personaje``); los valores ``None`` se ignoran.

    Returns:
        FichaPersonaje: Ficha actualizada.

    Raises:
        ErrorNoEncontrado: Si la ficha o el AU destino no existen.
        AppException: Si la ficha o el AU destino no pertenecen al
            usuario (403).
        ErrorDatosInvalidos: Si no se envían datos, o si ``edad`` no es
            válida para el AU destino.
    """
    ficha: FichaPersonaje | None = ficha_personaje_repository.obtener_ficha_por_id(
        db=db, id_ficha=id_ficha
    )
    if not ficha:
        raise ErrorNoEncontrado("Ficha de personaje")
    if ficha.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para modificar esta ficha.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )

    if "id_au" in kwargs and kwargs["id_au"] is not None:
        au: Au | None = au_repository.obtener_au_por_id(db=db, id_au=kwargs["id_au"])
        if not au:
            raise ErrorNoEncontrado("AU")
        if au.id_usuario != id_usuario:
            raise AppException(
                mensaje="Error: No tienes permiso para usar este AU.",
                codigo_http=status.HTTP_403_FORBIDDEN,
            )
        au_destino = au
    else:
        au_destino = ficha.au

    if "edad" in kwargs and kwargs["edad"] is not None:
        if "idols" not in au_destino.nombre_au.lower():
            raise ErrorDatosInvalidos(
                mensaje="Error: La edad solo está permitida en el AU 'idols'."
            )
        if kwargs["edad"] <= 0:
            raise ErrorDatosInvalidos(mensaje="Error: La edad debe ser mayor a 0.")

    datos = {k: v for k, v in kwargs.items() if v is not None}
    if not datos:
        raise ErrorDatosInvalidos(
            mensaje="Error: No se enviaron datos para actualizar."
        )
    id_au_ficha = ficha.id_au

    ficha_actualizada = ficha_personaje_repository.actualizar_ficha(
        db=db, ficha=ficha, datos=datos
    )

    prefijos = {
        f"fichas:usuario:{id_usuario}:None:",
        f"fichas:usuario:{id_usuario}:{id_au_ficha}:",
    }
    if "id_au" in datos and datos["id_au"] != id_au_ficha:
        prefijos.add(f"fichas:usuario:{id_usuario}:{datos["id_au"]}:")
    invalidar_cache_por_prefijo(*prefijos)

    return ficha_actualizada


def eliminar_ficha(db: Session, id_ficha: uuid.UUID, id_usuario: uuid.UUID) -> None:
    """Elimina una ficha propia e invalida la cache asociada.

    Args:
        db: Sesión de base de datos.
        id_ficha: Identificador UUID de la ficha a eliminar.
        id_usuario: Identificador UUID del usuario propietario esperado.

    Raises:
        ErrorNoEncontrado: Si la ficha no existe.
        AppException: Si la ficha pertenece a otro usuario (403).
    """
    ficha: FichaPersonaje | None = ficha_personaje_repository.obtener_ficha_por_id(
        db=db, id_ficha=id_ficha
    )
    if not ficha:
        raise ErrorNoEncontrado("Ficha de personaje")
    if ficha.id_usuario != id_usuario:
        raise AppException(
            mensaje="Error: No tienes permiso para eliminar esta ficha.",
            codigo_http=status.HTTP_403_FORBIDDEN,
        )
    id_ficha_au = ficha.id_au

    ficha_personaje_repository.eliminar_ficha(db=db, ficha=ficha)
    invalidar_cache_por_prefijo(
        f"fichas:usuario:{id_usuario}:None:",
        f"fichas:usuario:{id_usuario}:{id_ficha_au}:",
    )


def subir_imagen_ficha(
    db: Session,
    id_usuario: uuid.UUID,
    imagen: UploadFile,
    id_ficha: uuid.UUID | None = None,
) -> str:
    """Sube una imagen a Cloudinary y, opcionalmente, la asocia a una ficha.

    Si se indica ``id_ficha``, se verifica que la ficha exista y
    pertenezca al usuario antes de usar su id como ``public_id``
    determinístico en Cloudinary.

    Args:
        db: Sesión de base de datos.
        id_usuario: Identificador UUID del usuario propietario esperado.
        imagen: Archivo de imagen a subir.
        id_ficha: Identificador de la ficha a asociar, o ``None`` para
            subir la imagen sin asociarla a ninguna ficha.

    Returns:
        str: URL segura (``secure_url``) de la imagen subida.

    Raises:
        ErrorDatosInvalidos: Si el tipo de imagen no está permitido.
        ErrorNoEncontrado: Si ``id_ficha`` no corresponde a ninguna
            ficha.
        AppException: Si la ficha no pertenece al usuario (403).
    """
    if imagen.content_type not in TIPOS_PERMITIDOS:
        raise ErrorDatosInvalidos(mensaje="Error: Tipo de imagen no permitido.")
    public_id = None
    if id_ficha is not None:
        obtener_ficha_por_id(db=db, id_ficha=id_ficha, id_usuario=id_usuario)
        public_id = str(id_ficha)
    return subir_imagen(imagen=imagen.file, public_id=public_id)


def remover_imagen(
    db: Session, id_ficha: uuid.UUID, id_usuario: uuid.UUID
) -> FichaPersonaje:
    """Quita la imagen de una ficha en base de datos y en Cloudinary.

    Args:
        db: Sesión de base de datos.
        id_ficha: Identificador UUID de la ficha.
        id_usuario: Identificador UUID del usuario propietario esperado.

    Returns:
        FichaPersonaje: Ficha sin imagen asociada.

    Raises:
        ErrorNoEncontrado: Si la ficha no existe.
        AppException: Si la ficha pertenece a otro usuario (403).
    """
    ficha = obtener_ficha_por_id(db=db, id_ficha=id_ficha, id_usuario=id_usuario)
    if ficha.url_imagen:
        ficha_personaje_repository.limpiar_imagen(db=db, ficha=ficha)
        try:
            eliminar_imagen(public_id=str(id_ficha))
        except AppException:
            pass
    return ficha

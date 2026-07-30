"""Endpoints REST para universos alternos (AUs) y fichas anidadas."""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, status
from typing import Any, List, Annotated
from uuid import UUID

from src.schemas.au_schema import AuCreate, AuUpdate, AuResponse
from src.schemas.ficha_personaje_schema import FichaPersonajeResponse
from src.database.session import get_db
from src.services import au_service
from src.services import ficha_personaje_service
from src.utils.jwt_auth import verificar_admin, get_id_usuario

au_router: APIRouter = APIRouter(prefix="/aus", tags=["AUs"])


@au_router.get(
    path="/", status_code=status.HTTP_200_OK, response_model=List[AuResponse]
)
def obtener_aus_por_id_usuario(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    """Lista los AUs pertenecientes al usuario autenticado.

    Args:
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado, usado para obtener el id de
            usuario.
        skip: Cantidad de registros a omitir para paginación.
        limit: Cantidad máxima de registros a devolver.

    Returns:
        list[AuResponse]: AUs del usuario autenticado.
    """
    return au_service.obtener_aus_por_usuario(
        db=db, id_usuario=get_id_usuario(payload=payload), skip=skip, limit=limit
    )


@au_router.get(
    path="/buscar", status_code=status.HTTP_200_OK, response_model=AuResponse
)
def obtener_au_por_nombre(
    nombre_au: str,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    """Busca un AU por nombre dentro de los AUs del usuario autenticado.

    Args:
        nombre_au: Nombre exacto del AU a buscar.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        AuResponse: AU encontrado.

    Raises:
        ErrorDatosInvalidos: Si ``nombre_au`` está vacío.
        ErrorNoEncontrado: Si no existe un AU con ese nombre para el
            usuario.
    """
    return au_service.obtener_au_por_nombre(
        db=db, id_usuario=get_id_usuario(payload=payload), nombre_au=nombre_au
    )


@au_router.get(
    path="/{id_au}", status_code=status.HTTP_200_OK, response_model=AuResponse
)
def obtener_au_por_id(
    id_au: UUID,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    """Obtiene un AU por su UUID verificando que pertenezca al usuario.

    Args:
        id_au: Identificador UUID del AU.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        AuResponse: AU solicitado.

    Raises:
        ErrorNoEncontrado: Si no existe un AU con ese id.
        AppException: Si el AU no pertenece al usuario autenticado (403).
    """
    return au_service.obtener_au_por_id(
        db=db, id_au=id_au, id_usuario=get_id_usuario(payload=payload)
    )


@au_router.get(
    path="/{id_au}/fichas",
    status_code=status.HTTP_200_OK,
    response_model=List[FichaPersonajeResponse],
)
def obtener_fichas_de_au(
    id_au: UUID,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    """Lista las fichas de personaje pertenecientes al AU indicado.

    Args:
        id_au: Identificador UUID del AU cuyas fichas se listarán.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        list[FichaPersonajeResponse]: Fichas asociadas al AU.

    Raises:
        ErrorNoEncontrado: Si el AU no existe.
        AppException: Si el AU no pertenece al usuario autenticado (403).
    """
    return ficha_personaje_service.obtener_fichas_por_au(
        db=db, id_usuario=get_id_usuario(payload=payload), id_au=id_au
    )


@au_router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=AuResponse
)
def crear_au(
    datos: AuCreate,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    """Crea un nuevo universo alterno para el usuario autenticado.

    Args:
        datos: Datos de entrada con ``nombre_au`` y ``descripcion_au``.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        AuResponse: AU recién creado.

    Raises:
        ErrorDatosInvalidos: Si no se proporciona un nombre.
        AppException: Si ya existe un AU con el mismo nombre (409).
    """
    return au_service.crear_au(
        db=db,
        id_usuario=get_id_usuario(payload=payload),
        nombre_au=datos.nombre_au,
        descripcion_au=datos.descripcion_au,
    )


@au_router.patch(
    path="/{id_au}", status_code=status.HTTP_200_OK, response_model=AuResponse
)
def actualizar_au(
    id_au: UUID,
    datos: AuUpdate,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    """Actualiza el nombre o la descripción de un AU propio.

    Args:
        id_au: Identificador UUID del AU a actualizar.
        datos: Campos a modificar; los valores ``None`` se ignoran.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Returns:
        AuResponse: AU actualizado.

    Raises:
        ErrorNoEncontrado: Si el AU no existe.
        AppException: Si el AU no pertenece al usuario, o si el nuevo
            nombre colisiona con otro AU existente (403/409).
        ErrorDatosInvalidos: Si no se envía ningún dato para actualizar.
    """
    return au_service.actualizar_au(
        db=db,
        id_au=id_au,
        id_usuario=get_id_usuario(payload=payload),
        **datos.model_dump(exclude_none=True),
    )


@au_router.delete(path="/{id_au}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_au(
    id_au: UUID,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict[str, Any], Depends(verificar_admin)],
):
    """Elimina un AU propio del usuario autenticado.

    Args:
        id_au: Identificador UUID del AU a eliminar.
        db: Sesión de base de datos inyectada por dependencia.
        payload: Payload del JWT verificado.

    Raises:
        ErrorNoEncontrado: Si el AU no existe.
        AppException: Si el AU no pertenece al usuario autenticado (403).
    """
    au_service.eliminar_au(
        db=db, id_au=id_au, id_usuario=get_id_usuario(payload=payload)
    )

# Gestor de Fichas de Personajes

API REST para administrar universos alternos (AUs) y fichas de personajes
propios, pensada como herramienta personal de *worldbuilding*. Permite
organizar personajes por universo narrativo, adjuntarles imágenes y
consultarlos mediante distintos criterios de búsqueda (nombre, signo
zodiacal, sexo, cumpleaños).

Es una aplicación de un solo usuario administrador (por el momento): no hay registro
público ni multiusuario, todo el acceso está protegido por autenticación
JWT.

## Tabla de contenidos

- [Stack tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Modelo de datos y reglas de negocio](#modelo-de-datos-y-reglas-de-negocio)
- [Endpoints principales](#endpoints-principales)
- [Cacheo con Redis](#cacheo-con-redis)
- [Manejo de imágenes](#manejo-de-imágenes)
- [Instalación](#instalación)
- [Variables de entorno](#variables-de-entorno)
- [Migraciones](#migraciones)
- [Testing](#testing)
- [Despliegue](#despliegue)

## Stack tecnológico

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) como framework web (ASGI, sobre Starlette).
- [SQLAlchemy 2.x](https://www.sqlalchemy.org/) (`Mapped` / `mapped_column`) como ORM.
- [PostgreSQL](https://www.postgresql.org/) alojado en [Neon](https://neon.tech/).
- [Alembic](https://alembic.sqlalchemy.org/) para migraciones.
- [Pydantic 2](https://docs.pydantic.dev/) para validación y serialización.
- [Argon2](https://github.com/hynek/argon2-cffi) para el hasheo de contraseñas.
- [PyJWT](https://pyjwt.readthedocs.io/) para autenticación basada en JWT (access + refresh token).
- [Redis](https://redis.io/) para cacheo de listados (patrón *cache-aside*).
- [Cloudinary](https://cloudinary.com/) para almacenamiento de imágenes.

**Frontend**
- Angular con TypeScript y SCSS.
- Interceptor HTTP con renovación automática de tokens.

**Infraestructura**
- Backend desplegado en [Render](https://render.com/).
- Frontend desplegado en [Firebase Hosting](https://firebase.google.com/products/hosting).

## Arquitectura

El backend sigue una arquitectura en capas:

```
routers → services → repositories → models
```

- **Routers**: definen los endpoints, validan el esquema de entrada/salida
  con Pydantic y delegan toda la lógica a la capa de servicios.
- **Services**: contienen las reglas de negocio (permisos, validaciones,
  invalidación de cache, integración con Cloudinary).
- **Repositories**: funciones planas (no clases) que reciben una `Session`
  y encapsulan el acceso a la base de datos.
- **Models**: entidades SQLAlchemy 2.x, con `__init__` manual y
  `from __future__ import annotations` + `TYPE_CHECKING` para evitar
  importaciones circulares.

## Modelo de datos y reglas de negocio

Tablas principales: `usuarios`, `aus`, `fichas_personajes`.

- Un `Usuario` tiene muchos `Au` y muchas `FichaPersonaje`.
- Un `Au` tiene muchas `FichaPersonaje`.
- `UNIQUE(id_usuario, nombre_au)`: no puede haber dos AUs con el mismo
  nombre para un mismo usuario.
- `ON DELETE RESTRICT` en `au_id`: no se puede eliminar un AU que aún
  tenga fichas asociadas.
- Pueden existir fichas con el mismo nombre en distintos AUs.
- El campo `edad` solo está permitido cuando el AU se llama `"idols"`;
  en cualquier otro AU debe ser `null`.

## Endpoints principales

Todos los endpoints (excepto `/auth/login` y `/auth/refresh`) requieren un
JWT válido de un usuario administrador.

**Auth**
- `POST /auth/login`
- `POST /auth/refresh`

**Usuarios**
- `GET /usuarios/me`
- `POST /usuarios/`
- `PATCH /usuarios/me`
- `DELETE /usuarios/me`

**AUs**
- `GET /aus/`
- `GET /aus/buscar?nombre_au=`
- `GET /aus/{id_au}`
- `GET /aus/{id_au}/fichas`
- `POST /aus/`
- `PATCH /aus/{id_au}`
- `DELETE /aus/{id_au}`

**Fichas de personaje**
- `GET /fichas/`
- `GET /fichas/{id_ficha}`
- `GET /fichas/buscar/nombre`
- `GET /fichas/buscar/signo`
- `GET /fichas/buscar/sexo`
- `GET /fichas/buscar/cumpleanos`
- `GET /fichas/buscar/cumpleanos/dia`
- `GET /fichas/buscar/cumpleanos/mes`
- `POST /fichas/`
- `POST /fichas/upload-image`
- `POST /fichas/remove-image`
- `PATCH /fichas/{id_ficha}`
- `DELETE /fichas/{id_ficha}`

## Cacheo con Redis

Los listados de AUs y fichas (`/aus/`, `/fichas/`, `/aus/{id_au}/fichas`)
usan un patrón *cache-aside*:

1. Se busca la respuesta en Redis con una clave que incluye
   `id_usuario`, `id_au` (cuando aplica), `skip` y `limit`.
2. Si hay un resultado cacheado, se devuelve directamente.
3. Si no, se consulta la base de datos, se guarda el resultado
   serializado en Redis y se devuelve.

Toda operación de escritura (crear, actualizar, eliminar) invalida las
entradas relacionadas mediante coincidencia de prefijo de clave.

## Manejo de imágenes

Las imágenes de las fichas se almacenan en Cloudinary usando el
`id_ficha_personaje` como `public_id` determinístico (`overwrite=True`,
`invalidate=True`), lo que permite reemplazar la imagen de una ficha sin
generar recursos huérfanos. Al eliminar la imagen de una ficha, se limpia
tanto la referencia en base de datos como el recurso en Cloudinary.

## Instalación

```bash
git clone <url-del-repositorio>
cd gestor-de-fichas-de-personajes
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt


Levantar el servidor en modo desarrollo:

```bash
uvicorn api_config:app --reload
```

> `api_config.py` vive en la raíz del proyecto (no dentro de `src/`)
> porque así lo requiere la forma en que Uvicorn resuelve el import.

## Variables de entorno

Crear un archivo `.env` en la raíz del proyecto con, al menos:

```
DATABASE_URL=postgresql+psycopg://usuario:password@host/dbname
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=
REFRESH_TOKEN_EXPIRE_DAYS=
REDIS_URL=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

## Migraciones

```bash
alembic revision --autogenerate -m "descripción del cambio"
alembic upgrade head
```

## Testing

```bash
pytest --cov
```

Se recomienda usar `pytest-mock` para simular dependencias externas
(Cloudinary, Redis) y `pytest-asyncio` para los casos que lo requieran.

## Despliegue

- **Backend**: Render, usando `gunicorn` con workers de Uvicorn como
  servidor de producción.
- **Frontend**: Firebase Hosting.
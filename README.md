# Gestor Fichas API

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.140+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?logo=postgresql&logoColor=white)](https://neon.tech/)
[![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media-3448C5?logo=cloudinary&logoColor=white)](https://cloudinary.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-138%20passing-brightgreen?logo=pytest&logoColor=white)](https://docs.pytest.org/)

API REST desarrollada con **FastAPI** para la administración de universos alternos (*Alternative Universes* o **AUs**) y fichas de personajes de rol, concebida como herramienta de *worldbuilding* y gestión creativa. Permite estructurar y catalogar personajes por universo narrativo, almacenar imágenes en la nube, gestionar enlaces de música temática y realizar búsquedas avanzadas por múltiples criterios.

El acceso y las operaciones de administración se encuentran protegidos mediante autenticación **OAuth2 con JWT** (tokens de acceso y refresco).

---

## Tabla de contenidos

1. [Características principales](#características-principales)
2. [Stack tecnológico](#stack-tecnológico)
3. [Estructura del directorio](#estructura-del-directorio)
4. [Catálogo de Endpoints](#catálogo-de-endpoints)
5. [Autenticación y Seguridad](#autenticación-y-seguridad)
6. [Caché con Redis](#caché-con-redis)
7. [Gestión multimedia (Cloudinary)](#gestión-multimedia-cloudinary)
8. [Variables de entorno](#variables-de-entorno)
9. [Instalación y ejecución local](#instalación-y-ejecución-local)
10. [Ejecución con Docker](#ejecución-con-docker)
11. [Migraciones con Alembic](#migraciones-con-alembic)
12. [Testing y Cobertura](#testing-y-cobertura)
13. [Despliegue](#despliegue)

---

## Características principales

- **Gestión de Universos Alternos (AUs)**: Creación, consulta paginada, edición y eliminación de universos asociados a cada usuario administrador.
- **Fichas de Personaje completas**: Atributos como nombre, sexo, fecha de cumpleaños, signo zodiacal, descripción, URLs multimedia (imágenes y enlaces de audio/música).
- **Búsquedas especializadas**:
  - Por coincidencia de nombre de personaje.
  - Por signo zodiacal.
  - Por sexo.
  - Por fecha exacta de cumpleaños (`YYYY-MM-DD`).
  - Por día específico del mes (1 a 31).
  - Por mes de cumpleaños (1 a 12).
- **Estrategia de Caché de Alto Rendimiento**: Implementación de *cache-aside* en listados con Redis y degradación tolerante a fallos si Redis no está activo.
- **Gestión determinística de imágenes**: Subida a Cloudinary con `public_id` basado en el UUID de la ficha, permitiendo reemplazo automático sin dejar archivos huérfanos.
- **Documentación OpenAPI interactiva**: Swagger UI y ReDoc autogenerados.

---

## Stack tecnológico

### Backend
- **Lenguaje**: Python 3.12+
- **Framework Web**: [FastAPI](https://fastapi.tiangolo.com/) (0.140+)
- **Servidor ASGI/WSGI**: [Uvicorn](https://www.uvicorn.org/) y [Gunicorn](https://gunicorn.org/)
- **ORM**: [SQLAlchemy 2.x](https://www.sqlalchemy.org/) con tipado moderno (`Mapped`, `mapped_column`)
- **Driver de BD**: [psycopg 3](https://www.psycopg.org/psycopg3/) (`psycopg[binary]`)
- **Base de Datos**: [PostgreSQL](https://www.postgresql.org/) en la nube ([Neon](https://neon.tech/))
- **Migraciones**: [Alembic](https://alembic.sqlalchemy.org/)
- **Validación y Esquemas**: [Pydantic v2](https://docs.pydantic.dev/)
- **Seguridad**: [Argon2](https://github.com/hynek/argon2-cffi) (`argon2-cffi`) para hasheo de contraseñas y [PyJWT](https://pyjwt.readthedocs.io/) para tokens JWT
- **Caché**: [Redis](https://redis.io/) con `hiredis`
- **Almacenamiento en la nube**: [Cloudinary](https://cloudinary.com/)
- **Testing**: [Pytest](https://docs.pytest.org/), `pytest-cov`, `pytest-mock`, `pytest-asyncio`, `pytest-xdist`, `HTTPX` y SQLite en memoria (`StaticPool`)

### Frontend & Despliegue
- **Frontend**: Aplicación Angular con TypeScript y SCSS desplegada en [Firebase Hosting](https://firebase.google.com/products/hosting) (`https://coche-biblioteca-70aa7.web.app`).
- **Backend Host**: [Render](https://render.com/).
- **Contenedores**: Docker (imagen `python:3.12-slim`).

---

## Estructura del directorio

```text
gestor-fichas-personaje-api/
├── alembic/                      # Configuración y versiones de migraciones de base de datos
│   ├── versions/                 # Scripts de migración generados
│   └── env.py                    # Entorno de ejecución de Alembic
├── src/
│   ├── database/                 # Conexión, motor y fábrica de sesiones SQLAlchemy
│   │   ├── base.py               # Declaración de Base y creación inicial de tablas
│   │   ├── engine.py             # Configuración del Engine
│   │   └── session.py            # Generador get_db para inyección de dependencias
│   ├── entities/                 # Modelos ORM (tablas)
│   │   ├── usuario.py            # Entidad Usuario
│   │   ├── au.py                 # Entidad Au (Universo Alterno)
│   │   └── ficha_personaje.py    # Entidad FichaPersonaje
│   ├── exceptions/               # Excepciones personalizadas y manejadores globales
│   │   ├── excepciones.py        # Clases de excepción del dominio
│   │   └── exception_handlers.py # Registro de handlers en FastAPI
│   ├── repositories/             # Capa de persistencia (queries a BD)
│   │   ├── usuario_repository.py
│   │   ├── au_repository.py
│   │   └── ficha_personaje_repository.py
│   ├── routers/                  # Controladores REST organizados por recurso
│   │   ├── auth_router.py        # /auth (login, refresh)
│   │   ├── usuario_router.py     # /usuarios (me, crud)
│   │   ├── au_router.py          # /aus (crud, filtros, fichas anidadas)
│   │   └── ficha_personaje_router.py # /fichas (crud, búsquedas, subida de imagen)
│   ├── schemas/                  # Modelos Pydantic (Request/Response DTOs)
│   │   ├── auth_schema.py
│   │   ├── usuario_schema.py
│   │   ├── au_schema.py
│   │   └── ficha_personaje_schema.py
│   ├── services/                 # Capa de lógica de negocio
│   │   ├── usuario_service.py
│   │   ├── au_service.py
│   │   └── ficha_personaje_service.py
│   ├── utils/                    # Utilidades y servicios auxiliares
│   │   ├── caching_redis.py      # Cliente Redis y funciones cache-aside
│   │   ├── hash_password.py      # Hasheo y verificación con Argon2
│   │   ├── image_manager.py      # Subida y borrado en Cloudinary
│   │   └── jwt_auth.py           # Creación, verificación y renovación de JWT
│   └── tests/                    # Suite completa de tests unitarios y de integración
│       ├── conftest.py           # Fixtures compartidas (SQLite en memoria, cliente HTTP, tokens)
│       ├── repository-test/      # Tests directos sobre la capa de repositorio
│       ├── service-test/         # Tests de la lógica de servicios
│       └── routers-test/         # Tests de integración sobre endpoints HTTP
├── api_config.py                 # Factoría y configuración de la app FastAPI, CORS y ciclo de vida
├── main.py                       # Punto de entrada para ejecución local con Uvicorn
├── alembic.ini                   # Configuración global de Alembic
├── dockerfile                    # Definición de contenedor Docker de producción
├── .dockerignore                 # Archivos excluidos del contexto Docker
├── pytest.ini                    # Configuración de ejecución de Pytest
├── requirements.txt              # Dependencias fijadas del proyecto
└── README.md                     # Documentación general
```

---

## Catálogo de Endpoints

La documentación interactiva se encuentra disponible en:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Estado de salud
| Método | Endpoint | Descripción | Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/health` | Chequeo de operatividad de la API (`{"status": "ok"}`) | No |

---

### Autenticación (`/auth`)
| Método | Endpoint | Descripción | Código | Auth |
| :--- | :--- | :--- | :---: | :---: |
| `POST` | `/auth/login` | Login mediante OAuth2 Password Form (`username`, `password`). Emite access y refresh tokens. | `200` | No |
| `POST` | `/auth/refresh` | Emite un nuevo par de tokens a partir de un `refresh_token` válido. | `200` | No |

---

### Usuarios (`/usuarios`)
| Método | Endpoint | Descripción | Código | Auth |
| :--- | :--- | :--- | :---: | :---: |
| `GET` | `/usuarios/me` | Obtiene el perfil del usuario administrador autenticado. | `200` | JWT |
| `POST` | `/usuarios/` | Registra un nuevo usuario en el sistema. | `201` | JWT (Admin) |
| `PATCH` | `/usuarios/me` | Actualiza datos del perfil autenticado (nombre o contraseña). | `200` | JWT |
| `DELETE` | `/usuarios/me` | Elimina la cuenta del usuario autenticado. | `204` | JWT |

---

### Universos Alternos (`/aus`)
| Método | Endpoint | Descripción | Código | Auth |
| :--- | :--- | :--- | :---: | :---: |
| `GET` | `/aus/` | Lista los AUs del usuario (parámetros `skip` y `limit`, cacheado en Redis). | `200` | JWT |
| `GET` | `/aus/buscar?nombre_au=` | Busca un AU del usuario por coincidencia exacta de nombre. | `200` | JWT |
| `GET` | `/aus/{id_au}` | Obtiene el detalle de un AU por su UUID. | `200` | JWT |
| `GET` | `/aus/{id_au}/fichas` | Lista todas las fichas de personajes asociadas a un AU (cacheado en Redis). | `200` | JWT |
| `POST` | `/aus/` | Crea un nuevo universo alterno (`nombre_au`, `descripcion_au`). | `201` | JWT |
| `PATCH` | `/aus/{id_au}` | Actualiza el nombre o la descripción de un AU existente. | `200` | JWT |
| `DELETE` | `/aus/{id_au}` | Elimina un AU (rechaza si posee fichas asociadas). | `204` | JWT |

---

### Fichas de Personaje (`/fichas`)
| Método | Endpoint | Descripción | Código | Auth |
| :--- | :--- | :--- | :---: | :---: |
| `GET` | `/fichas/` | Lista todas las fichas del usuario autenticado (paginación `skip`, `limit`, cacheado). | `200` | JWT |
| `GET` | `/fichas/{id_ficha}` | Obtiene el detalle de una ficha por su UUID. | `200` | JWT |
| `GET` | `/fichas/buscar/nombre?nombre_personaje=` | Busca fichas por nombre de personaje (paginado). | `200` | JWT |
| `GET` | `/fichas/buscar/signo?signo_zodiacal=` | Busca fichas por signo zodiacal (paginado). | `200` | JWT |
| `GET` | `/fichas/buscar/sexo?sexo=` | Busca fichas por valor de sexo (paginado). | `200` | JWT |
| `GET` | `/fichas/buscar/cumpleanos?fecha_cumpleanos=` | Busca fichas por fecha exacta de cumpleaños (`YYYY-MM-DD`). | `200` | JWT |
| `GET` | `/fichas/buscar/cumpleanos/dia?dia=` | Busca fichas con cumpleaños en un día del mes (`1-31`). | `200` | JWT |
| `GET` | `/fichas/buscar/cumpleanos/mes?mes=` | Busca fichas con cumpleaños en un mes (`1-12`). | `200` | JWT |
| `POST` | `/fichas/` | Crea una nueva ficha de personaje asociada a un AU. | `201` | JWT |
| `POST` | `/fichas/upload-image` | Sube imagen a Cloudinary (multipart/form-data). Admite vincular `id_ficha` por query param. | `200` | JWT |
| `POST` | `/fichas/remove-image` | Elimina la imagen de una ficha tanto en BD como en Cloudinary (`id_ficha`). | `200` | JWT |
| `PATCH` | `/fichas/{id_ficha}` | Modifica los datos de una ficha existente. | `200` | JWT |
| `DELETE` | `/fichas/{id_ficha}` | Elimina una ficha de personaje. | `204` | JWT |

---

## Autenticación y Seguridad

- **Hasheo seguro**: Las contraseñas se almacenan mediante **Argon2**, inmunes a ataques de diccionario y colisiones comunes.
- **Flujo de Tokens**:
  - Al iniciar sesión en `/auth/login`, se valida el usuario y contraseña y se genera un par de tokens:
    - **Access Token**: Token de corta duración para autorización en cabecera `Authorization: Bearer <token>`.
    - **Refresh Token**: Token de mayor vigencia para renovar el par sin requerir reingresar credenciales.
- **Extracción segura**: Las rutas protegidas validan el payload del token (`sub`, `nombre_usuario`, `es_admin`) mediante la dependencia `verificar_admin`.

---

## Caché con Redis

Se utiliza una estrategia **Cache-Aside**:
1. Para peticiones de listados (`/aus/`, `/fichas/`, `/aus/{id_au}/fichas`), se calcula una clave única basada en el usuario y los parámetros de paginación (`skip`, `limit`).
2. Si la clave reside en Redis, se deserializa el JSON y se entrega de inmediato evitando consultas a la base de datos.
3. Si la clave no existe (o expira su TTL de 120 segundos), se realiza la consulta a PostgreSQL, se serializa el resultado en Redis y se entrega al cliente.
4. **Invalidación proactiva**: Toda acción de creación, actualización o eliminación elimina las claves cacheadas mediante prefijos (`invalidar_cache_por_prefijo`), garantizando consistencia.
5. **Degradación silenciosa**: Si Redis no se encuentra disponible o se produce un error de conexión, el módulo captura `RedisError` y la aplicación continúa funcionando directamente con la base de datos sin interrumpir el servicio.

---

## Gestión multimedia (Cloudinary)

- **Subida de archivos**: Mediante `multipart/form-data` a través del endpoint `/fichas/upload-image`.
- **Tipos de archivo permitidos**: `image/jpg`, `image/jpeg`, `image/png`, `image/webp`.
- **Estrategia determinística**: Si se suministra un `id_ficha`, se utiliza dicho UUID como `public_id` en la carpeta `fichas_personajes` de Cloudinary con `overwrite=True` e `invalidate=True`. Esto garantiza que al actualizar la imagen de una ficha se sobreescriba en el CDN sin acumular imágenes huérfanas.
- **Borrado síncrono**: Al llamar a `/fichas/remove-image` o actualizar la imagen, se asegura el borrado del recurso remoto.

---

## Variables de entorno

Cree un archivo `.env` en la raíz del proyecto. A continuación se presentan las variables requeridas por los módulos del sistema:

```ini
# --- Base de Datos (PostgreSQL en Neon o Local) ---
DATABASE_URL=postgresql+psycopg://<usuario>:<password>@<host>/<dbname>?sslmode=require

# --- Autenticación y JWT ---
JWT_KEY=tu_clave_secreta_super_segura
ALGORITHM=algoritmo_de_seleccion
ACCESS_TOKEN_EXPIRE=60          # Minutos de expiración del token de acceso
REFRESH_TOKEN_EXPIRE=7          # Días de expiración del token de refresco

# --- Almacenamiento en Cloudinary ---
CLOUDINARY_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# --- Caché en Redis ---
REDIST_HOST_NAME=tu_redis_host   # Host o endpoint de Redis
REDIS_PORT=6379                 # Puerto de Redis
REDIS_USERNAME=default          # Opcional según el proveedor
REDIS_PASSWORD=tu_redis_password # Contraseña de Redis
```

---

## Instalación y ejecución local

### Requisitos previos
- **Python 3.12+** instalado.
- Servidor **PostgreSQL** o instancia de Neon DB.
- Instancia de **Redis** (local o en la nube, opcional para desarrollo).

### 1. Clonar el repositorio
```bash
git clone https://github.com/sebastiant01/gestor-fichas-personaje-api.git
cd gestor-fichas-personaje-api
```

### 2. Crear y activar el entorno virtual
En Linux / macOS:
```bash
python -m venv .venv
source .venv/bin/activate
```
En Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copie o cree el archivo `.env` en la raíz con sus credenciales siguiendo el ejemplo de la sección [Variables de entorno](#variables-de-entorno).

### 5. Iniciar la aplicación en modo desarrollo
Puede iniciar el servidor directamente mediante el script `main.py`:
```bash
python main.py
```
O ejecutando Uvicorn directamente con recarga en vivo:
```bash
uvicorn api_config:app --host 0.0.0.0 --port 8000 --reload
```

> **Nota**: `api_config.py` reside en la raíz del proyecto para permitir una resolución limpia y directa de la instancia ASGI `api_config:app` por parte de Uvicorn y Gunicorn.

---

## Ejecución con Docker

El proyecto incluye un `dockerfile` listo para producción con Python 3.12-slim:

### 1. Construir la imagen Docker
```bash
docker build -t gestor-fichas-api .
```

### 2. Ejecutar el contenedor
```bash
docker run -d \
  --name gestor-fichas-api \
  -p 8000:8000 \
  --env-file .env \
  gestor-fichas-api
```

La API responderá en `http://localhost:8000` con la documentación en `http://localhost:8000/docs`.

---

## Migraciones con Alembic

Para gestionar la evolución del esquema en PostgreSQL:

### Crear una nueva migración automática:
```bash
alembic revision --autogenerate -m "descripcion_del_cambio"
```

### Aplicar las migraciones a la base de datos:
```bash
alembic upgrade head
```

### Revertir la última migración:
```bash
alembic downgrade -1
```

---

## Testing y Cobertura

La suite de pruebas automatizadas está compuesta por **138 tests** que cubren repositorios, servicios y endpoints REST.

Las pruebas utilizan una base de datos **SQLite en memoria** (`sqlite:///:memory:`) con `StaticPool`, garantizando pruebas rápidas, aisladas y sin alterar la base de datos de desarrollo o producción.

### Ejecutar todos los tests:
```bash
pytest
```

### Ejecutar tests con reporte de cobertura de código:
```bash
pytest --cov=src
```

### Ejecución en paralelo con `pytest-xdist`:
```bash
pytest -n auto
```

---

## Despliegue

### Backend en Render
- **Configuración de servicio**: Web Service en [Render](https://render.com/).
- **Comando de inicio**:
  ```bash
  gunicorn -k uvicorn.workers.UvicornWorker api_config:app --bind 0.0.0.0:$PORT
  ```
- **Variables de entorno**: Cargar en el panel de Render las variables detalladas en [Variables de entorno](#variables-de-entorno).

### CORS y Frontend
La API incluye configuración de `CORSMiddleware` en `api_config.py` admitiendo peticiones desde:
- `http://localhost:4200` (Entorno de desarrollo local de Angular).
- `https://coche-biblioteca-70aa7.web.app` (Aplicación en producción desplegada en Firebase Hosting).


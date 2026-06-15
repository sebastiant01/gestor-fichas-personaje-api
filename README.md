# coche-biblioteca# Coche Biblioteca — Back-End

API REST para la gestión de fichas de personaje de rol de mesa, agrupadas por universos alternos (AUs). Construida con FastAPI y PostgreSQL.

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Framework | FastAPI `0.111.0` + Uvicorn `0.30.1` |
| ORM | SQLAlchemy `2.0.30` (estilo `Mapped` / `mapped_column`) |
| Migraciones | Alembic `1.13.1` |
| Base de datos | PostgreSQL (Neon) — driver `psycopg[binary] 3.3.1` |
| Autenticación | JWT (`PyJWT 2.13.0`) + Argon2 (`argon2-cffi 25.1.0`) |
| Validación | Pydantic `2.12.5` |
| Testing | pytest `8.2.2` + httpx `0.27.0` + pytest-asyncio / mock / cov |

---

## Estructura del proyecto

```
coche-biblioteca-backend/
│
├── api_config.py              # Configuración de la app FastAPI (raíz del proyecto)
├── main.py
├── pytest.ini
├── alembic.ini
├── alembic/
│   └── env.py
├── .env
│
└── src/
    ├── database/
    │   ├── base.py
    │   ├── engine.py
    │   └── session.py
    │
    ├── entities/              # Modelos SQLAlchemy
    │   ├── au.py
    │   ├── ficha_personaje.py
    │   └── usuario.py
    │
    ├── exceptions/
    │   ├── excepciones.py
    │   └── exception_handlers.py
    │
    ├── repositories/
    │   ├── au_repository.py
    │   ├── ficha_personaje_repository.py
    │   └── usuario_repository.py
    │
    ├── routers/
    │   ├── au_router.py
    │   ├── auth_router.py
    │   ├── ficha_personaje_router.py
    │   └── usuario_router.py
    │
    ├── schemas/
    │   ├── au_schema.py
    │   ├── auth_schema.py
    │   ├── ficha_personaje_schema.py
    │   └── usuario_schema.py
    │
    ├── services/
    │   ├── au_service.py
    │   ├── ficha_personaje_service.py
    │   └── usuario_service.py
    │
    ├── utils/
    │   ├── hash_password.py
    │   └── jwt_auth.py
    │
    └── tests/
        ├── conftest.py
        ├── repository-test/
        │   ├── test_au.py
        │   ├── test_ficha_personaje.py
        │   └── test_usuario.py
        ├── routers-test/
        │   ├── test_au.py
        │   ├── test_auth.py
        │   ├── test_ficha_personaje.py
        │   └── test_usuario.py
        └── service-test/
            ├── test_au.py
            ├── test_ficha_personaje.py
            └── test_usuario.py
```

### Patrón de capas

```
Router → Service → Repository → Entidad (SQLAlchemy)
```

Cada capa tiene una única responsabilidad. Los routers no acceden a los repositorios directamente; los servicios contienen todas las reglas de negocio.

---

## Modelos de datos

### `usuarios`

| Columna | Tipo | Notas |
|---|---|---|
| `id_usuario` | UUID | PK, generado automáticamente |
| `nombre_usuario` | VARCHAR(40) | UNIQUE |
| `contrasena_hash` | TEXT | Argon2 |
| `es_admin` | BOOLEAN | `default=False` |
| `fecha_creacion` | TIMESTAMPTZ | `server_default=now()` |
| `fecha_edicion` | TIMESTAMPTZ | `onupdate=now()`, nullable |

### `aus` (universos alternos)

| Columna | Tipo | Notas |
|---|---|---|
| `id_au` | UUID | PK |
| `id_usuario` | UUID | FK → `usuarios` |
| `nombre_au` | VARCHAR(50) | UNIQUE por usuario (`uq_au_usuario_nombre`) |
| `descripcion_au` | TEXT | nullable |
| `fecha_creacion` | TIMESTAMPTZ | `server_default=now()` |
| `fecha_edicion` | TIMESTAMPTZ | `onupdate=now()`, nullable |

### `fichas_personajes`

| Columna | Tipo | Notas |
|---|---|---|
| `id_ficha_personaje` | UUID | PK |
| `id_usuario` | UUID | FK → `usuarios` |
| `id_au` | UUID | FK → `aus` (`ON DELETE RESTRICT`) |
| `nombre_personaje` | VARCHAR(100) | |
| `sexo` | VARCHAR(30) | |
| `edad` | SMALLINT | nullable; solo válida en AUs llamados `"idols"` |
| `fecha_cumpleanos` | DATE | |
| `signo_zodiacal` | VARCHAR(20) | nullable |
| `descripcion_personaje` | TEXT | nullable |
| `url_imagen` | TEXT | nullable |
| `url_musica` | TEXT | nullable |
| `fecha_creacion` | TIMESTAMPTZ | `server_default=now()` |
| `fecha_edicion` | TIMESTAMPTZ | `onupdate=now()`, nullable |

---

## Autenticación

La API usa un esquema de **usuario administrador** (`es_admin=True`). Todos los endpoints protegidos requieren un JWT válido.

### Flujo

1. `POST /auth/login` con credenciales → devuelve `access_token`.
2. El token se incluye en la cabecera `Authorization: Bearer <token>`.
3. La dependencia `verificar_admin` valida el token y extrae el `id_usuario` del claim `sub`.

### Endpoints de autenticación

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/auth/login` | Inicia sesión y devuelve el JWT |

---

## Endpoints

Todos los endpoints siguientes requieren autenticación.

### Universos Alternos (`/aus`)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/aus` | Lista todos los AUs del usuario |
| `POST` | `/aus` | Crea un nuevo AU |
| `GET` | `/aus/{id_au}` | Obtiene un AU por ID |
| `PUT` | `/aus/{id_au}` | Actualiza un AU |
| `DELETE` | `/aus/{id_au}` | Elimina un AU (falla si tiene fichas asociadas) |

### Fichas de Personaje (`/fichas`)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/fichas` | Lista todas las fichas del usuario |
| `POST` | `/fichas` | Crea una nueva ficha |
| `GET` | `/fichas/{id_ficha_personaje}` | Obtiene una ficha por ID |
| `PUT` | `/fichas/{id_ficha_personaje}` | Actualiza una ficha |
| `DELETE` | `/fichas/{id_ficha_personaje}` | Elimina una ficha |

---

## Reglas de negocio

- El campo `edad` solo es válido en fichas pertenecientes a un AU llamado `"idols"`. En cualquier otro AU, `edad` se almacena como `NULL` independientemente de lo que se envíe.
- No se pueden eliminar AUs que tengan fichas asociadas (`ON DELETE RESTRICT`).
- No se pueden crear dos AUs con el mismo nombre para el mismo usuario (constraint `uq_au_usuario_nombre`).
- Sí se pueden crear fichas con el mismo nombre de personaje en AUs distintos.
- El `id_usuario` nunca se expone en los schemas de request; se extrae siempre del JWT.

---

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
DATABASE_URL=postgresql+psycopg://usuario:contraseña@host/nombre_bd
SECRET_KEY=tu_clave_secreta_para_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> **Nota:** `api_config.py` debe estar en la raíz del proyecto (fuera de `src/`) por requerimientos de resolución de módulos de uvicorn.

---

## Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd coche-biblioteca-backend

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\Activate.ps1      # Windows PowerShell

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Crear el archivo .env con las variables indicadas arriba

# 5. Ejecutar migraciones
alembic upgrade head

# 6. Iniciar el servidor
uvicorn api_config:app --reload
```

La API estará disponible en `http://localhost:8000`. La documentación interactiva en `http://localhost:8000/docs`.

---

## Testing

Los tests están organizados en tres capas: repositorios, servicios y routers. Se usa SQLite en memoria con `pytest` y `httpx` como cliente de pruebas.

```bash
# Ejecutar todos los tests
pytest

# Con reporte de cobertura
pytest --cov=src

# Output detallado
pytest -v
```

---

## Decisiones de diseño notables

- **Repositorios como funciones puras:** Los repositorios no son clases; son funciones que reciben una `Session` como parámetro, lo que facilita el testing y la inyección de dependencias.
- **`__init__` manual en entidades:** Cada entidad define su propio `__init__` para mejorar el autocompletado del IDE, ya que SQLAlchemy no lo genera por defecto con el estilo `Mapped`.
- **`from __future__ import annotations` + `TYPE_CHECKING`:** Se usa en las entidades para evitar importaciones circulares entre relaciones bidireccionales.
- **Excepciones personalizadas:** Todas las excepciones de negocio están centralizadas en `excepciones.py` con sus manejadores correspondientes en `exception_handlers.py`, permitiendo respuestas HTTP consistentes.
- **Schemas Pydantic v2:** Los schemas de respuesta usan `ConfigDict(from_attributes=True)` para compatibilidad con instancias ORM.
- **Utilidades separadas:** La lógica de hashing (`hash_password.py`) y JWT (`jwt_auth.py`) vive en `utils/`, desacoplada de los servicios.
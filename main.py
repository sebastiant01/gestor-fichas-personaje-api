"""
Punto de entrada para ejecutar el servidor de desarrollo con Uvicorn.

Uso::

    python main.py

Documentación interactiva (Swagger): http://127.0.0.1:8000/docs
"""

import uvicorn

from api_config import app

if __name__ == "__main__":
    # reload exige el string de importación; `app` sigue disponible para tests / ASGI
    uvicorn.run(
        "api_config:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

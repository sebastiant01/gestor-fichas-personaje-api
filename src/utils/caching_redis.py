"""
Cliente Redis opcional para cachear listados JSON de AUs y fichas.

Si Redis no está disponible, las funciones fallan en silencio y la app sigue
consultando la base de datos.
"""

from redis import RedisError, Redis
import os
import json
from dotenv import load_dotenv
from typing import Optional, Any

load_dotenv()

redis: Redis = Redis(
    host=os.getenv("REDIST_HOST_NAME", ""),
    port=int(os.getenv("REDIS_PORT", 0)),
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=10,
    username=os.getenv("REDIS_USERNAME"),
    password=os.getenv("REDIS_PASSWORD"),
)


def obtener_respuesta_cache(cache_key: str) -> Optional[list[dict[str, Any]]]:
    """Lee y deserializa una lista cacheada; ``None`` si no hay entrada o hay error."""
    try:
        respuesta_json = redis.get(name=cache_key)
        if respuesta_json:
            return json.loads(respuesta_json)
    except RedisError:
        pass


def guardar_respuesta_cache(
    cache_key: str, valor: str, ttl_segundos: int = 120
) -> None:
    """Guarda JSON en Redis con TTL por defecto de 120 segundos."""
    try:
        redis.set(name=cache_key, value=valor, ex=ttl_segundos)
    except RedisError:
        pass


def invalidar_cache(*keys: str) -> None:
    """Elimina claves concretas del cache."""
    try:
        if keys:
            redis.delete(*keys)
    except RedisError:
        pass


def invalidar_cache_por_prefijo(*prefijos: str) -> None:
    """Elimina todas las claves que empiezan por cada prefijo dado."""
    try:
        for prefijo in prefijos:
            keys = redis.keys(f"{prefijo}*")
            if keys:
                redis.delete(*keys)
    except RedisError:
        pass

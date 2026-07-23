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
    try:
        respuesta_json = redis.get(name=cache_key)
        if respuesta_json:
            return json.loads(respuesta_json)
    except RedisError:
        pass


def guardar_respuesta_cache(
    cache_key: str, valor: str, ttl_segundos: int = 120
) -> None:
    try:
        redis.setex(name=cache_key, time=ttl_segundos, value=valor)
    except RedisError:
        pass


def invalidar_cache(*keys: str) -> None:
    try:
        if keys:
            redis.delete(*keys)
    except RedisError:
        pass


def invalidar_cache_por_prefijo(*prefijos: str) -> None:
    try:
        for prefijo in prefijos:
            keys = redis.keys(f"{prefijo}*")
            if keys:
                redis.delete(*keys)
    except RedisError:
        pass

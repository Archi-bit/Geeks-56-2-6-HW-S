from django.core.cache import caches
from typing import Optional

CACHE_ALIAS = "default"
REDIS_PREFIX = "confirmation_code"
TTL_SECONDS = 300

def _key(user_id: int) -> str:
    return f"{REDIS_PREFIX}:{user_id}"

def set_confirmation_code(user_id: int, code: str) -> None:

    cache = caches[CACHE_ALIAS]
    cache.set(_key(user_id), code, timeout=TTL_SECONDS)

def get_confirmation_code(user_id: int) -> Optional[str]:

    cache = caches[CACHE_ALIAS]
    val = cache.get(_key(user_id))
    return val

def delete_confirmation_code(user_id: int) -> None:
    cache = caches[CACHE_ALIAS]
    cache.delete(_key(user_id))

def check_and_delete_confirmation_code(user_id: int, provided_code: str) -> int:

    cache = caches[CACHE_ALIAS]
    key = _key(user_id)

    try:
        client = cache.client.get_client(write=True)
    except Exception:
        val = cache.get(key)
        if val is None:
            return -1
        if str(val) == provided_code:
            cache.delete(key)
            return 1
        return 0

    lua = """
    local val = redis.call('GET', KEYS[1])
    if not val then
        return -1
    end
    if val == ARGV[1] then
        redis.call('DEL', KEYS[1])
        return 1
    end
    return 0
    """
    try:
        res = client.eval(lua, 1, key, provided_code)
        return int(res)
    except Exception:
        val = cache.get(key)
        if val is None:
            return -1
        if str(val) == provided_code:
            cache.delete(key)
            return 1
        return 0

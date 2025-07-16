import hashlib
import json
from redis import asyncio as aioredis
from fastapi import Request

from functools import wraps
from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.variables import REDIS_URL
from src.decorators.jwt import decode_jwt_token, extract_token_from_request

redis = aioredis.from_url(REDIS_URL, decode_responses=True)


def generate_cache_key(request: Request) -> str:
    token = extract_token_from_request(request)
    payload = decode_jwt_token(token)
    user_id = payload.get("sub", "anonymous")

    base = {
        "user": user_id,
        "method": request.method,
        "path": request.url.path,
        "query": dict(request.query_params),
    }
    raw_key = json.dumps(base, sort_keys=True)
    return f"cache:{hashlib.sha256(raw_key.encode()).hexdigest()}"


async def get_cached_response(key: str):
    return await redis.get(key)


async def set_cached_response(key: str, data: dict, ttl: int = 60):
    await redis.set(key, data, ex=ttl)


def cache_response(ttl: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if not request:
                raise ValueError("Request is required for caching")

            cache_key = generate_cache_key(request)
            cached = await get_cached_response(cache_key)
            if cached:
                return JSONResponse(
                    content=json.loads(cached), headers={"X-Cache-Status": "HIT"}
                )

            response = await func(*args, **kwargs)
            # if response is not of JSONResponse we avoid caching it.
            if isinstance(response, JSONResponse) and response.status_code == 200:
                await set_cached_response(cache_key, response.body.decode(), ttl)

            response.headers["X-Cache-Status"] = "MISS"
            return response

        return wrapper

    return decorator

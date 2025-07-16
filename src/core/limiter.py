from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.variables import REDIS_URL


def user_key_func(request: Request):
    if hasattr(request.state, "user"):
        return str(request.state.user.uid)
    return get_remote_address(request)


limiter = Limiter(
    key_func=user_key_func,
    storage_uri=REDIS_URL,
    headers_enabled=True,
)

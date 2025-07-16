from slowapi.util import get_remote_address
from slowapi import Limiter
from functools import wraps
from fastapi import Request, HTTPException, status

from slowapi.util import get_remote_address

from src.core.variables import REDIS_URL

PLAN_LIMITS = {
    "basic": "5/day",
    "pro": "1000/day",
}


def user_key_func(request: Request):
    if hasattr(request.state, "user"):
        return str(request.state.user.uid)
    return get_remote_address(request)


limiter = Limiter(
    key_func=user_key_func,
    storage_uri=REDIS_URL,
    headers_enabled=True,
)


def rate_limit_by_plan(limiter: Limiter):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")

            if not request or not hasattr(request.state, "user"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )

            user_plan_list = getattr(request.state.user, "plan", [])
            active_plan = next((p for p in user_plan_list if p.active), None)
            user_tier = getattr(active_plan, "plan", "basic").lower()

            limit = PLAN_LIMITS.get(user_tier.lower(), PLAN_LIMITS["basic"])

            decorated_func = limiter.limit(limit)(func)
            return await decorated_func(*args, **kwargs)

        return wrapper

    return decorator

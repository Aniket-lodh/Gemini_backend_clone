from functools import wraps
import traceback
from fastapi import status, HTTPException
from sqlmodel import Session
from src.utils.format_response import format_response


def catch_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db_pool: Session | None = kwargs.get("db_pool", None)

        try:
            if db_pool and not db_pool.in_transaction():
                db_pool.begin()

            result = await func(*args, **kwargs)

            if db_pool and db_pool.in_transaction():
                db_pool.rollback()

            return result

        except Exception as e:
            traceback.print_exc()
            print("\n💥 Exception caught at catch_async::", str(e))

            if db_pool and db_pool.in_transaction():
                db_pool.rollback()

            if isinstance(e, HTTPException):
                return format_response(status_code=e.status_code, message=e.detail)

            return format_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Something went wrong. Please try again later.",
            )

    return wrapper

from functools import wraps
from fastapi import HTTPException, Request, status
from sqlmodel import Session
from jose import JWTError, jwt
import time
import traceback
from typing import Optional
from src.core.db_models import TableNameEnum
from src.core.db_methods import DB

from src.utils.format_response import format_response
from src.core.variables import JWT_SECRET

db = DB()


def authentication_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # try:
        db_pool: Session = kwargs.get("db_pool")
        request: Request = kwargs.get("request")

        if not request:
            raise HTTPException(
                detail="Request object not found in kwargs",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Retrieve Authorization header and then extract token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                detail="Missing or invalid Authorization header.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            sub: str = payload.get("sub")

            if not sub:
                raise JWTError("Invalid payload structure")

        except JWTError as e:
            print("JWT decode error:", e)
            raise HTTPException(
                detail="Invalid or expired token.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # Optionally check if the user is still active in DB
        exist_user = await db.get_attr(
            dbClassName=TableNameEnum.Users,
            uid=sub,
            db_pool=db_pool,
        )
        if not exist_user or exist_user.disabled is True:
            raise HTTPException(
                detail="User account is inactive or invalid.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        elif exist_user.confirmed is False:
            raise HTTPException(
                detail="Verify account to continue.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        request.state.user = exist_user

        return await func(*args, **kwargs)

    return wrapper

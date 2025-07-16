from datetime import datetime, timedelta
from typing import Any, Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlmodel import Session
from src.core.db_pool import DataBasePool
from src.core.db_models import TableNameEnum
from src.api.authentication import schemas
import src.core.variables as variables
from src.core.db_methods import DB
from src.utils.format_response import format_response
from src.utils.security import hash_password, verify_password


db = DB()


async def register_user(
    user_create: schemas.UserCreate, db_pool: Session
) -> schemas.UserSchema:
    """Registers a new user."""
    existing_user = await db.get_attr(
        dbClassName=TableNameEnum.Users,
        mobile_number=user_create.mobile_number,
        db_pool=db_pool,
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mobile number already registered",
        )
    created_user, ok = await db.insert(
        dbClassName=TableNameEnum.Users,
        data=user_create.model_dump(exclude="password"),
        db_pool=db_pool,
    )
    if ok is False:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register, please try again later.",
        )

    _, ok = await db.insert(
        dbClassName=TableNameEnum.Password,
        data={"uid": created_user.uid, "password": hash_password(user_create.password)},
        db_pool=db_pool,
    )
    if ok is False:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register, please try again later.",
        )

    # Creating a basic plan for user by default.
    _, ok = await db.insert(
        dbClassName=TableNameEnum.UserPlan,
        data={
            "user_id": created_user.uid,
            "active": True,
            "plan": "basic",
        },
        db_pool=db_pool,
    )
    if ok is False:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register, please try again later.",
        )

    db_pool.commit()
    return format_response(
        message="User registered",
        data=schemas.UserSchema(**created_user.model_dump()).model_dump(),
    )


async def generate_otp(mobile_number: str, db_pool: Session) -> str:
    """Generates a mock OTP."""
    existing_user = await db.get_attr(
        dbClassName=TableNameEnum.Users,
        mobile_number=mobile_number,
        db_pool=db_pool,
    )
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mobile number",
        )
    return format_response(
        message="OTP sent", data=schemas.OTPResponse(otp="123456").model_dump()
    )


async def verify_otp(otp_verification: schemas.OTPVerification, db_pool: Session):
    """Verifies the OTP and returns a JWT token."""
    existing_user = await db.get_attr(
        dbClassName=TableNameEnum.Users,
        mobile_number=otp_verification.mobile_number,
        db_pool=db_pool,
    )
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mobile number",
        )

    if otp_verification.otp != "123456":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP"
        )

    _, ok = await db.update(
        dbClassName=TableNameEnum.Users,
        data={**existing_user.model_dump(), "confirmed": True},
        db_pool=db_pool,
        commit=True,
    )
    if ok is False:
        raise HTTPException(
            detail="Failed to verify user, try again later",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    token = create_jwt_token(data={"sub": str(existing_user.uid)})
    return format_response(
        message="OTP verified successfully.",
        data=schemas.Token(access_token=token, token_type="bearer").model_dump(),
    )


def create_jwt_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Creates a JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, variables.JWT_SECRET, algorithm="HS256")
    return encoded_jwt


async def get_current_user(
    token: str = "change",
    db_pool: Session = Depends(DataBasePool.get_pool),
):
    """Retrieves the currently authenticated user from the JWT token."""
    try:
        payload = jwt.decode(token, variables.JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = await db.get_attr(
        dbClassName=TableNameEnum.Users, uid=user_id, db_pool=db_pool
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


async def change_password(
    user_id: str,
    change_password: schemas.ChangePassword,
    db_pool: Session,
):
    user = await db.get_attr(
        dbClassName=TableNameEnum.Users, uid=user_id, db_pool=db_pool
    )
    if not user or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user or password not set",
        )

    if not verify_password(
        change_password.old_password,
        user.password.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password"
        )

    # Validating if user is trying to set the same old password as new password
    if verify_password(change_password.new_password, user.password.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the old password",
        )

    try:
        user.password.password = hash_password(change_password.new_password)
        db_pool.add(user.password)
        db_pool.commit()
    except Exception:
        raise HTTPException(
            detail="Failed to update password",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return format_response(message="Password changed successfully")

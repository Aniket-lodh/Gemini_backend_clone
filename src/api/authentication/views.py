from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from src.decorators.auth_required import authentication_required
from src.decorators.catch_async import catch_async
from src.core.db_pool import DataBasePool

from src.api.authentication import schemas, services

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    description="Registers a new user with mobile number and optional info.",
)
@catch_async
async def signup(
    user_create: schemas.UserCreate, db_pool: Session = Depends(DataBasePool.get_pool)
):
    return await services.register_user(user_create, db_pool)


@router.post(
    "/send-otp",
    description="Sends an OTP to the user's mobile number (mocked, returned in response).",
)
@catch_async
async def send_otp(
    mobile_number: schemas.MobileNumber,
    db_pool: Session = Depends(DataBasePool.get_pool),
):
    return await services.generate_otp(mobile_number.mobile_number, db_pool)


@router.post(
    "/verify-otp",
    description="Verifies the OTP and returns a JWT token for the session.",
)
@catch_async
async def verify_otp(
    otp_verification: schemas.OTPVerification,
    db_pool: Session = Depends(DataBasePool.get_pool),
):
    return await services.verify_otp(otp_verification, db_pool)


@router.post("/forgot-password", description="Sends OTP for password reset.")
@catch_async
async def forgot_password(
    mobile_number: schemas.MobileNumber,
    db_pool: Session = Depends(DataBasePool.get_pool),
):
    return await services.generate_otp(mobile_number.mobile_number, db_pool)


@router.post("/reset-password", description="Reset password using OTP verification")
@catch_async
async def reset_password(
    payload: schemas.ResetPassword,
    db_pool: Session = Depends(DataBasePool.get_pool),
):
    return await services.reset_password(payload, db_pool)


@router.post(
    "/change-password",
    description="Allows the user to change password while logged in.",
)
@catch_async
@authentication_required
async def change_password(
    request: Request,
    change_password: schemas.ChangePassword,
    db_pool: Session = Depends(DataBasePool.get_pool),
):
    return await services.change_password(
        request.state.user.uid, change_password, db_pool
    )

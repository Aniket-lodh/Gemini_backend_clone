from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from src.decorators.auth_required import authentication_required
from src.decorators.catch_async import catch_async
from src.core.db_pool import DataBasePool

from src.api.user import schemas, services

router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "/me",
    description="Returns details of the currently logged in user",
    response_model=schemas.UserSchema,
)
@catch_async
@authentication_required
async def me(
    request: Request, db_pool: Session = Depends(DataBasePool.get_pool)
):
    return await services.me(request.state.user.uid, db_pool)

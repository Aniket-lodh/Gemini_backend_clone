from fastapi import HTTPException, status
from sqlmodel import Session
from src.core.db_methods import DB
from src.api.user import schemas
from src.core.db_models import TableNameEnum
from src.utils.format_response import format_response

db = DB()


async def me(user_id: str, db_pool: Session):
    """Registers a new user."""
    existing_user = await db.get_attr(
        dbClassName=TableNameEnum.Users,
        uid=user_id,
        db_pool=db_pool,
    )
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return format_response(
        message="User retrieved.",
        data=schemas.UserSchema(**existing_user.model_dump()).model_dump(),
    )

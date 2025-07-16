from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.core.db_models import TableNameEnum
from src.core.db_methods import DB
from src.api.chatroom import schemas
from src.celery import service
from src.utils.format_response import format_response

db = DB()


async def create_chatroom(
    user_id: str, chatroom_create: schemas.ChatroomCreate, db_pool: Session
):
    """Creates a new chatroom for the given user."""
    created_chatroom, ok = await db.insert(
        dbClassName=TableNameEnum.Chatrooms,
        data={"owner_id": user_id, **chatroom_create.model_dump()},
        db_pool=db_pool,
    )
    if ok is False:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chatroom, please try again later.",
        )
    db_pool.commit()
    return schemas.ChatroomCreate(**created_chatroom.model_dump())


async def list_chatrooms(user_id: str, db_pool: Session) -> List[schemas.Chatroom]:
    """Lists all chatrooms for a specific user."""
    existing_chatrooms = await db.get_attr_all(
        dbClassName=TableNameEnum.Chatrooms, uid=user_id, db_pool=db_pool
    )
    return format_response(
        message="Chatrooms retrieved.",
        data=[chatroom.model_dump() for chatroom in existing_chatrooms],
    )


async def get_chatroom(
    chatroom_id: int, user_id: int, db_pool: Session
) -> schemas.Chatroom:
    """Retrieves a specific chatroom, ensuring the user has access."""
    existing_chatroom = await db.get_attr(
        dbClassName=TableNameEnum.Chatrooms, chatroom_id=chatroom_id, db_pool=db_pool
    )
    if not existing_chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chatroom not found"
        )
    if existing_chatroom.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this chatroom",
        )
    return existing_chatroom


async def send_message(
    chatroom_id: int, user_id: int, payload: schemas.MessageCreate, db_pool: Session
) -> None:
    """Sends a message to a chatroom and enqueues a Gemini API call."""
    chatroom = await get_chatroom(
        chatroom_id, user_id, db_pool
    )  # Ensure user has access

    created_message_record, ok = await db.insert(
        dbClassName=TableNameEnum.Messages,
        data={
            "chatroom_id": chatroom.chatroom_id,
            "sender_id": user_id,
            **payload.model_dump(),
        },
        db_pool=db_pool,
    )
    if ok is False:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message, please try again later.",
        )
    service.enqueue_gemini_call(
        message_id=created_message_record.mid,
        message_text=payload.text,
    )
    db_pool.commit()
    return format_response(message="Message sent and processing.")


async def process_gemini_response(
    message_id: str, response_text: str, db_pool: Session
) -> None:
    """Processes the Gemini API response and stores it as a new message."""
    existing_message = await db.get_attr(
        dbClassName=TableNameEnum.Messages, mid=message_id, db_pool=db_pool
    )
    if existing_message is None:
        raise HTTPException(
            detail="Message not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    elif existing_message.status == "processed":
        raise HTTPException(
            detail="Message already processed.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    _, ok = await db.update(
        dbClassName=TableNameEnum.Messages,
        data={
            **existing_message.model_dump(),
            "response": response_text,
            "status": "processed",
        },
        db_pool=db_pool,
    )
    if ok is False:
        raise HTTPException(
            detail="Failed to process Gemini response, please try again later.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    db_pool.commit()

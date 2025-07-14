from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException

from src.api.authentication import schemas as auth_schemas, services as auth_services
from src.api.chatroom import schemas, services

router = APIRouter(prefix="/chatroom", tags=["Chatroom"])


@router.post("/")
async def create_chatroom(
    user: auth_schemas.User = Depends(auth_services.get_current_user),
) -> schemas.Chatroom:
    """Creates a new chatroom for the authenticated user."""
    chatroom = await services.create_chatroom(user.id)
    return chatroom


@router.get("/", response_model=List[schemas.Chatroom])
async def list_chatrooms(
    user: auth_schemas.User = Depends(auth_services.get_current_user),
) -> Any:
    """Lists all chatrooms for the user (use caching here)."""
    chatrooms = await services.list_chatrooms(user.id)
    return chatrooms


@router.get("/{id}", response_model=schemas.Chatroom)
async def get_chatroom(
    id: int, user: auth_schemas.User = Depends(auth_services.get_current_user)
) -> Any:
    """Retrieves detailed information about a specific chatroom."""
    chatroom = await services.get_chatroom(id, user.id)
    return chatroom


@router.post("/{id}/message")
async def send_message(
    id: int,
    message: schemas.MessageCreate,
    user: auth_schemas.User = Depends(auth_services.get_current_user),
) -> dict[str, str]:
    """Sends a message and receives a Gemini response (via queue/async call)."""
    await services.send_message(id, user.id, message.text)
    return {"message": "Message sent and processing."}
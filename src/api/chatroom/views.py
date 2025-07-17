from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from src.api.chatroom import schemas, services
from src.core.db_pool import DataBasePool
from src.decorators.auth_required import authentication_required
from src.decorators.catch_async import catch_async
from src.core.limiter import limiter, rate_limit_by_plan
from src.utils.caching import cache_response
from src.utils.format_response import format_response


router = APIRouter(prefix="/chatroom", tags=["Chatroom"])


@router.post("/", description="Creates a new chatroom for the authenticated user.")
@catch_async
@authentication_required
async def create_chatroom(
    request: Request,
    payload: schemas.ChatroomCreate,
    db_pool: Session = Depends(DataBasePool.get_pool),
):
    return await services.create_chatroom(request.state.user.uid, payload, db_pool)


@router.get(
    "/",
    description="Lists all chatrooms for the authenticated user.",
)
@catch_async
@cache_response(ttl=300)
@authentication_required
async def list_chatrooms(
    request: Request,
    db_pool: Session = Depends(DataBasePool.get_pool),
):
    return await services.list_chatrooms(request.state.user.uid, db_pool)


@router.get(
    "/{id}",
    description="Retrieves detailed information about a specific chatroom, including its messages.",
)
@catch_async
@authentication_required
async def get_chatroom(
    id: str,
    request: Request,
    db_pool: Session = Depends(DataBasePool.get_pool),
):
    return await services.get_chatroom_with_messages(id, request.state.user.uid, db_pool)


@router.post("/{id}/message", description="Sends a message to a specific chatroom.")
@catch_async
@authentication_required
@rate_limit_by_plan(limiter)
async def send_message(
    id: str,
    request: Request,
    payload: schemas.MessageCreate,
    db_pool: Session = Depends(DataBasePool.get_pool),
):
    return await services.send_message(id, request.state.user.uid, payload, db_pool)

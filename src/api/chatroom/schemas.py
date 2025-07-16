from typing import Optional
from pydantic import BaseModel


class Chatroom(BaseModel):
    chatroom_id: str
    name: str
    owner_id: str
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class ChatroomCreate(BaseModel):
    name: Optional[str] = None


class MessageCreate(BaseModel):
    text: str


class Message(BaseModel):
    mid: str
    chatroom_id: str
    sender_id: str
    text: str
    response: Optional[str] = None
    status: str
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
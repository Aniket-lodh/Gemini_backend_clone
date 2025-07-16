from enum import Enum
from re import A
import time
from typing import List, Optional
from sqlalchemy import Column, Integer, func
from sqlmodel import Field, Relationship, SQLModel

from src.core.security import Security, TokenType


class TableNameEnum(str, Enum):
    Users = "users"
    UserProfile = "user_profile"
    Chatrooms = "chatrooms"
    Messages = "messages"
    Password = "password"
    UserPlan = "userplan"
    Transactions = "transactions"


class Users(SQLModel, table=True):
    uid: str = Field(
        primary_key=True,
        index=True,
        default_factory=lambda: Security.generate_unique_id(type=TokenType.UUID),
    )
    mobile_number: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=True)
    full_name: str = Field(nullable=True)
    disabled: bool = Field(default=False)
    confirmed: bool = Field(default=False)
    stripe_customer_id: str = Field(nullable=True)

    created_at: Optional[int] = Field(default_factory=lambda: int(time.time()))
    updated_at: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, onupdate=func.extract("epoch", func.now())),
    )

    chatrooms: List["Chatrooms"] = Relationship(back_populates="owner")
    password: "Password" = Relationship(back_populates="user")

    plan: "UserPlan" = Relationship(back_populates="user")
    transactions: List["Transactions"] = Relationship(back_populates="user")


class UserPlan(SQLModel, table=True):
    plan_id: str = Field(
        primary_key=True,
        index=True,
        default_factory=lambda: Security.generate_unique_id(type=TokenType.UUID),
    )
    user_id: str = Field(foreign_key="users.uid", index=True)
    active: bool
    plan: str
    created_at: Optional[int] = Field(default_factory=lambda: int(time.time()))

    user: "Users" = Relationship(back_populates="plan")


class Transactions(SQLModel, table=True):
    transaction_id: str = Field(
        primary_key=True,
        index=True,
        default_factory=lambda: Security.generate_unique_id(type=TokenType.URL_SAFE),
    )
    user_id: str = Field(foreign_key="users.uid", index=True, nullable=False)
    plan_id: Optional[str] = Field(
        foreign_key="userplan.plan_id", default=None, index=True, nullable=False
    )
    status: str = Field(nullable=False)
    amount: int = Field(nullable=False)
    mode: str

    created_at: Optional[int] = Field(default_factory=lambda: int(time.time()))
    expires_at: Optional[int] = Field(nullable=True)

    user: "Users" = Relationship(back_populates="transactions")


class Password(SQLModel, table=True):
    uid: str = Field(primary_key=True, foreign_key="users.uid", index=True)
    password: str = Field(nullable=False)
    updated_at: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, onupdate=func.extract("epoch", func.now())),
    )
    user: "Users" = Relationship(back_populates="password")


class UserProfile(SQLModel, table=True):
    upid: str = Field(
        primary_key=True,
        index=True,
        default_factory=lambda: Security.generate_unique_id(type=TokenType.URL_SAFE),
    )
    user_id: str = Field(foreign_key="users.uid", index=True, nullable=False)
    bio: str = Field(nullable=True)
    created_at: Optional[int] = Field(default_factory=lambda: int(time.time()))
    updated_at: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, onupdate=func.extract("epoch", func.now())),
    )


class Chatrooms(SQLModel, table=True):
    chatroom_id: str = Field(
        primary_key=True,
        index=True,
        default_factory=lambda: Security.generate_unique_id(type=TokenType.URL_SAFE),
    )
    owner_id: str = Field(foreign_key="users.uid", index=True, nullable=False)
    name: str = Field(nullable=True)
    created_at: Optional[int] = Field(default_factory=lambda: int(time.time()))
    updated_at: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, onupdate=func.extract("epoch", func.now())),
    )

    owner: "Users" = Relationship(back_populates="chatrooms")
    messages: List["Messages"] = Relationship(back_populates="chatroom")


class Messages(SQLModel, table=True):
    mid: str = Field(
        primary_key=True,
        index=True,
        default_factory=lambda: Security.generate_unique_id(type=TokenType.URL_SAFE),
    )
    chatroom_id: str = Field(foreign_key="chatrooms.chatroom_id")
    sender_id: str = Field(foreign_key="users.uid", index=True, nullable=False)
    text: str = Field(nullable=False)
    response: str = Field(nullable=True)
    status: str = Field(default="pending", nullable=False)
    created_at: Optional[int] = Field(default_factory=lambda: int(time.time()))
    updated_at: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, onupdate=func.extract("epoch", func.now())),
    )

    chatroom: "Chatrooms" = Relationship(back_populates="messages")

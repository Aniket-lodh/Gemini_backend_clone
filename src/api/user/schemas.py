from typing import Optional
from pydantic import BaseModel


class UserSchema(BaseModel):
    uid: str
    mobile_number: str
    email: str
    full_name: str
    disabled: bool
    confirmed: bool
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class UserProfile(BaseModel):
    upid: str
    user_id: str
    bio: str
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

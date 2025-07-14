from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, StringConstraints, constr, field_validator


class UserSchema(BaseModel):
    uid: str
    mobile_number: str
    email: str
    full_name: str
    disabled: bool
    confirmed: bool
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class UserCreate(BaseModel):
    mobile_number: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=10, max_length=15),
    ]
    email: Optional[EmailStr] = None
    full_name: Optional[
        Annotated[
            str,
            StringConstraints(strip_whitespace=True, max_length=100),
        ]
    ] = None
    password: Annotated[
        str,
        StringConstraints(min_length=8, max_length=128),
    ]

    @field_validator("mobile_number")
    def mobile_number_must_be_valid(cls, mobile_number: str) -> str:
        if not mobile_number.isdigit():
            raise ValueError("Mobile number must contain only digits")
        if not (10 <= len(mobile_number) <= 15):
            raise ValueError("Mobile number must be between 10 and 15 digits")
        return mobile_number

    @field_validator("password")
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if v.lower() == v or v.upper() == v:
            raise ValueError(
                "Password must include both uppercase and lowercase characters"
            )
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must include at least one number")
        return v


class MobileNumber(BaseModel):
    mobile_number: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=10, max_length=15),
    ]

    @field_validator("mobile_number")
    def mobile_number_must_be_valid(cls, mobile_number: str) -> str:
        if not mobile_number.isdigit():
            raise ValueError("Mobile number must contain only digits")
        if not (10 <= len(mobile_number) <= 15):
            raise ValueError("Mobile number must be between 10 and 15 digits")
        return mobile_number


class OTPResponse(BaseModel):
    otp: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=4, max_length=6),
    ]


class OTPVerification(BaseModel):
    mobile_number: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=10, max_length=15),
    ]
    otp: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=4, max_length=6),
    ]

    @field_validator("mobile_number")
    def mobile_number_must_be_valid(cls, mobile_number: str) -> str:
        if not mobile_number.isdigit():
            raise ValueError("Mobile number must contain only digits")
        if not (10 <= len(mobile_number) <= 15):
            raise ValueError("Mobile number must be between 10 and 15 digits")
        return mobile_number


class Token(BaseModel):
    access_token: str
    token_type: str


class ChangePassword(BaseModel):
    old_password: Annotated[
        str,
        StringConstraints(min_length=8, max_length=128),
    ]
    new_password: Annotated[
        str,
        StringConstraints(min_length=8, max_length=128),
    ]

    @field_validator("new_password")
    def validate_new_password_strength(cls, v: str) -> str:
        if v.lower() == v or v.upper() == v:
            raise ValueError(
                "New password must include both uppercase and lowercase characters"
            )
        if not any(char.isdigit() for char in v):
            raise ValueError("New password must include at least one number")
        return v

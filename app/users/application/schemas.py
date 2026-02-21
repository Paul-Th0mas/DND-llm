import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    picture_url: str
    role: str
    created_at: datetime


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    # Role is chosen at registration time: "dm" creates rooms, "player" joins them.
    role: Literal["dm", "player"] = "player"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

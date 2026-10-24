from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import UserRole


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    phone: str | None
    full_name: str
    role: UserRole
    email_verified: bool
    created_at: datetime

"""
===============================================================================
COSMOS Authentication Schemas

Pydantic schemas for authentication.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr


# --------------------------------------------------------------------------
# Request Schemas
# --------------------------------------------------------------------------

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


# --------------------------------------------------------------------------
# Response Schemas
# --------------------------------------------------------------------------

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
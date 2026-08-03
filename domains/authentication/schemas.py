"""
===============================================================================
COSMOS Authentication Schemas

Pydantic schemas for authentication.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_admin: bool
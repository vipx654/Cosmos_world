"""
===============================================================================
COSMOS Authentication Routes

Authentication API routes.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from fastapi import APIRouter
from fastapi import HTTPException

from database.session import SessionLocal
from domains.authentication.repositories import UserRepository
from domains.authentication.schemas import UserCreate, UserResponse
from domains.authentication.services import AuthenticationService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):

    db = SessionLocal()

    try:
        repository = UserRepository(db)
        service = AuthenticationService(repository)

        created_user = service.register(
            username=user.username,
            email=user.email,
            password_hash=user.password,
            full_name=user.full_name,
        )

        return created_user

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    finally:
        db.close()
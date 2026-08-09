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
from domains.authentication.schemas import UserCreate
from domains.authentication.schemas import UserResponse

from domains.license.repository import LicenseRepository
from domains.license.repository import DeviceRepository
from domains.license.services import LicenseService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(user: UserCreate):

    db = SessionLocal()

    try:

        user_repository = UserRepository(db)

        license_repository = LicenseRepository(db)
        device_repository = DeviceRepository(db)

        license_service = LicenseService(
            license_repository=license_repository,
            device_repository=device_repository,
        )

        auth_service = AuthenticationService(
            repository=user_repository,
            license_service=license_service,
        )

        created_user = auth_service.register(
            username=user.username,
            email=user.email,
            password_hash=user.password,
            full_name=user.full_name,
        )

        print("========== REGISTERED USER ==========")
        print(created_user)
        print(created_user.__dict__)

        return UserResponse(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            full_name=created_user.full_name,
            is_active=created_user.is_active,
            is_admin=created_user.is_admin,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    finally:
        db.close()
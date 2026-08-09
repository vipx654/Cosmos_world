"""
===============================================================================
COSMOS Authentication Routes

Authentication API

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from fastapi import APIRouter
from fastapi import HTTPException

from database.session import SessionLocal

from domains.authentication.repository import UserRepository
from domains.authentication.schemas import UserCreate
from domains.authentication.schemas import UserResponse
from domains.authentication.services import AuthenticationService

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
            password=user.password,
            full_name=user.full_name,
        )

        return UserResponse.model_validate(created_user)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    finally:

        db.close()
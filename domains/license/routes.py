"""
===============================================================================
COSMOS License Routes

API routes for the COSMOS Identity & License Service (CILS).

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from fastapi import APIRouter
from fastapi import HTTPException

from database.session import SessionLocal

from domains.license.repository import (
    LicenseRepository,
    DeviceRepository,
)

from domains.license.services import LicenseService

from domains.license.schemas import (
    DeviceRegister,
    DeviceResponse,
    LicenseResponse,
)

router = APIRouter(
    prefix="/license",
    tags=["License"],
)


@router.get("/{license_key}", response_model=LicenseResponse)
def get_license(
    license_key: str,
):
    db = SessionLocal()

    try:
        service = LicenseService(
            LicenseRepository(db),
            DeviceRepository(db),
        )

        license = service.validate_license(
            license_key
        )

        if not license:
            raise HTTPException(
                status_code=404,
                detail="License not found.",
            )

        return license

    finally:
        db.close()


@router.post(
    "/register-device",
    response_model=DeviceResponse,
)
def register_device(
    request: DeviceRegister,
):
    db = SessionLocal()

    try:
        service = LicenseService(
            LicenseRepository(db),
            DeviceRepository(db),
        )

        license = service.validate_license(
            request.license_key
        )

        if not license:
            raise HTTPException(
                status_code=404,
                detail="License not found.",
            )

        device = service.register_device(
            license=license,
            machine_id=request.machine_id,
            device_name=request.device_name,
            operating_system=request.operating_system,
            connector_version=request.connector_version,
        )

        return device

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    finally:
        db.close()
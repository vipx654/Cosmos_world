"""
===============================================================================
COSMOS License Schemas

Pydantic schemas for the COSMOS Identity & License Service (CILS).

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class LicenseCreate(BaseModel):
    """
    Create a new COSMOS license.
    """

    user_id: int

    license_type: str = Field(
        default="FREE",
        examples=["FREE", "PRO", "ENTERPRISE"],
    )

    max_devices: int = Field(
        default=1,
        ge=1,
    )


class LicenseResponse(BaseModel):
    """
    License information returned by the API.
    """

    id: int
    user_id: int
    cosmos_id: str
    license_key: str
    license_type: str
    status: str
    max_devices: int
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class DeviceRegister(BaseModel):
    """
    Register a new device.
    """

    license_key: str

    machine_id: str = Field(
        min_length=16,
        max_length=128,
    )

    device_name: str = Field(
        min_length=2,
        max_length=100,
    )

    operating_system: str = Field(
        min_length=2,
        max_length=50,
    )

    connector_version: str = Field(
        min_length=1,
        max_length=20,
    )


class DeviceResponse(BaseModel):
    """
    Registered device information.
    """

    id: int
    machine_id: str
    device_name: str
    operating_system: str
    connector_version: str
    is_active: bool

    class Config:
        from_attributes = True


class LicenseValidationRequest(BaseModel):
    """
    Connector authentication request.
    """

    license_key: str

    machine_id: str

    connector_version: str


class LicenseValidationResponse(BaseModel):
    """
    Result of license validation.
    """

    valid: bool

    message: str

    cosmos_id: Optional[str] = None

    license_type: Optional[str] = None

    jwt_token: Optional[str] = None
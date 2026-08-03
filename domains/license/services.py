"""
===============================================================================
COSMOS License Service

Business logic for the COSMOS Identity & License Service (CILS).

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from domains.license.models import License
from domains.license.models import RegisteredDevice

from domains.license.repository import DeviceRepository
from domains.license.repository import LicenseRepository

from core.license import generate_cosmos_id
from core.license import generate_license_key


class LicenseService:
    """
    Business logic for licenses.
    """

    def __init__(
        self,
        license_repository: LicenseRepository,
        device_repository: DeviceRepository,
    ):
        self.license_repository = license_repository
        self.device_repository = device_repository

    def create_license(
        self,
        user_id: int,
        license_type: str = "FREE",
        max_devices: int = 1,
    ) -> License:

        license = License(
            user_id=user_id,
            cosmos_id=generate_cosmos_id(),
            license_key=generate_license_key(),
            license_type=license_type,
            status="ACTIVE",
            max_devices=max_devices,
        )

        return self.license_repository.create(license)

    def validate_license(
        self,
        license_key: str,
    ) -> License | None:

        return self.license_repository.get_by_license_key(
            license_key
        )

    def register_device(
        self,
        license: License,
        machine_id: str,
        device_name: str,
        operating_system: str,
        connector_version: str,
    ) -> RegisteredDevice:

        active_devices = self.device_repository.count_active_devices(
            license.id
        )

        if active_devices >= license.max_devices:
            raise ValueError(
                "Maximum registered devices reached."
            )

        existing = self.device_repository.get_by_machine_id(
            machine_id
        )

        if existing:
            return existing

        device = RegisteredDevice(
            license_id=license.id,
            machine_id=machine_id,
            device_name=device_name,
            operating_system=operating_system,
            connector_version=connector_version,
        )

        return self.device_repository.create(device)
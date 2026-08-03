"""
===============================================================================
COSMOS License Repository

Database operations for the COSMOS Identity & License Service (CILS).

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from sqlalchemy.orm import Session

from domains.license.models import License
from domains.license.models import RegisteredDevice


class LicenseRepository:
    """
    Repository for License operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, license: License) -> License:
        self.db.add(license)
        self.db.commit()
        self.db.refresh(license)
        return license

    def get_by_license_key(self, license_key: str) -> License | None:
        return (
            self.db.query(License)
            .filter(License.license_key == license_key)
            .first()
        )

    def get_by_cosmos_id(self, cosmos_id: str) -> License | None:
        return (
            self.db.query(License)
            .filter(License.cosmos_id == cosmos_id)
            .first()
        )

    def get_by_user_id(self, user_id: int) -> License | None:
        return (
            self.db.query(License)
            .filter(License.user_id == user_id)
            .first()
        )


class DeviceRepository:
    """
    Repository for registered devices.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, device: RegisteredDevice) -> RegisteredDevice:
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def get_by_machine_id(
        self,
        machine_id: str,
    ) -> RegisteredDevice | None:
        return (
            self.db.query(RegisteredDevice)
            .filter(
                RegisteredDevice.machine_id == machine_id
            )
            .first()
        )

    def get_devices_by_license(
        self,
        license_id: int,
    ) -> list[RegisteredDevice]:
        return (
            self.db.query(RegisteredDevice)
            .filter(
                RegisteredDevice.license_id == license_id
            )
            .all()
        )

    def count_active_devices(
        self,
        license_id: int,
    ) -> int:
        return (
            self.db.query(RegisteredDevice)
            .filter(
                RegisteredDevice.license_id == license_id,
                RegisteredDevice.is_active.is_(True),
            )
            .count()
        )
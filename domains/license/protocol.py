"""
===============================================================================
COSMOS License Protocol

Interfaces used by the COSMOS Identity & License Service.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from typing import Protocol

from domains.license.models import License
from domains.license.models import RegisteredDevice


class LicenseProvider(Protocol):
    """
    Interface for license providers.
    """

    def validate_license(self, license_key: str) -> License | None:
        ...


class DeviceProvider(Protocol):
    """
    Interface for registered device providers.
    """

    def register_device(
        self,
        license: License,
        machine_id: str,
        device_name: str,
        operating_system: str,
        connector_version: str,
    ) -> RegisteredDevice:
        ...
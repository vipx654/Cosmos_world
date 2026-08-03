"""
===============================================================================
COSMOS License Exceptions

Custom exceptions for the COSMOS Identity & License Service (CILS).

Author: COSMOS Development Team
License: MIT
===============================================================================
"""


class LicenseError(Exception):
    """
    Base license exception.
    """

    pass


class LicenseNotFoundError(LicenseError):
    """
    License does not exist.
    """

    pass


class LicenseExpiredError(LicenseError):
    """
    License has expired.
    """

    pass


class LicenseBlockedError(LicenseError):
    """
    License has been blocked.
    """

    pass


class DeviceLimitExceededError(LicenseError):
    """
    Maximum number of registered devices reached.
    """

    pass


class DeviceAlreadyRegisteredError(LicenseError):
    """
    Device is already registered.
    """

    pass


class InvalidMachineError(LicenseError):
    """
    Machine fingerprint is invalid.
    """

    pass
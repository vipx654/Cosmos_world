"""
===============================================================================
COSMOS Authentication Exceptions

Custom exceptions for authentication.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""


class AuthenticationError(Exception):
    """Base authentication exception."""


class InvalidCredentials(AuthenticationError):
    """Invalid username or password."""


class UserAlreadyExists(AuthenticationError):
    """User already exists."""


class EmailAlreadyExists(AuthenticationError):
    """Email already exists."""
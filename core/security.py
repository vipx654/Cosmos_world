"""
===============================================================================
COSMOS Security

Password hashing utilities.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain password.
    """
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password against stored hash.
    """
    return pwd_context.verify(password, password_hash)
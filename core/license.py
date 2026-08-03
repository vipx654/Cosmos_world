"""
===============================================================================
COSMOS License Utilities

Utility functions for generating COSMOS identifiers and license keys.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

import secrets
import uuid


def generate_cosmos_id() -> str:
    """
    Generate a permanent COSMOS identity.
    """
    return f"COSMOS-{secrets.token_hex(4).upper()}"


def generate_license_key() -> str:
    """
    Generate a unique license key.
    """
    return f"COS-{uuid.uuid4()}".upper()


def generate_api_key() -> str:
    """
    Generate a secure API key.
    """
    return secrets.token_urlsafe(48)


def generate_machine_token() -> str:
    """
    Generate a unique machine token.
    """
    return secrets.token_hex(32).upper()
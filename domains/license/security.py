"""
===============================================================================
COSMOS License Security

Security helpers for the COSMOS Identity & License Service.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

import hashlib


def generate_machine_id(raw_fingerprint: str) -> str:
    """
    Generate a deterministic machine identifier.
    """

    return hashlib.sha256(
        raw_fingerprint.encode("utf-8")
    ).hexdigest().upper()
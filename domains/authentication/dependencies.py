"""
===============================================================================
COSMOS Authentication Dependencies

FastAPI dependency providers.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from database.session import SessionLocal


def get_db():
    """
    Database dependency.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
"""
===============================================================================
COSMOS Database Base

Provides the SQLAlchemy Declarative Base used by every model.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class inherited by all SQLAlchemy models.
    """

    pass
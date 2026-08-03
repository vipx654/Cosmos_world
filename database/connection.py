"""
===============================================================================
COSMOS Database Connection

Initializes the database and creates all registered tables.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from database.base import Base
from database.session import engine


def initialize_database() -> None:
    """
    Create all database tables registered with SQLAlchemy.
    """

    Base.metadata.create_all(bind=engine)
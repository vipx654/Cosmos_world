"""
===============================================================================
COSMOS Database Session

Creates and manages SQLAlchemy sessions.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
"""
===============================================================================
COSMOS Database Connection Manager

Handles SQLite database connection and SQLAlchemy session management.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------
# Database Location
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_FILE = BASE_DIR / "cosmos.db"

DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# ---------------------------------------------------------------------
# SQLAlchemy Engine
# ---------------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# ---------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# ---------------------------------------------------------------------
# Base Class
# ---------------------------------------------------------------------

Base = declarative_base()


def get_db():
    """
    Return a database session.

    Always closes the session after use.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
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

# ===========================
# Import ALL SQLAlchemy Models
# ===========================

from domains.authentication.models import User
from domains.license.models import License
from domains.license.models import RegisteredDevice

# Future models
# from domains.broker.models import Broker
# from domains.market.models import Market
# from domains.portfolio.models import Portfolio


def initialize_database() -> None:
    """
    Create all database tables.
    """
    Base.metadata.create_all(bind=engine)
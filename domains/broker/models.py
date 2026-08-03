"""
===============================================================================
COSMOS Broker Models

Database models for broker clients.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.base import Base


class BrokerClient(Base):
    """
    Registered Broker Client.
    """

    __tablename__ = "broker_clients"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    client_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    broker_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    online: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
"""
===============================================================================
COSMOS License Models

Database models for the COSMOS Identity & License Service (CILS).

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from database.base import Base


class License(Base):
    """
    Represents a COSMOS software license.
    """

    __tablename__ = "licenses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    cosmos_id: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    license_key: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    license_type: Mapped[str] = mapped_column(
        String(20),
        default="FREE",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="ACTIVE",
        nullable=False,
    )

    max_devices: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="licenses")

    devices = relationship(
        "RegisteredDevice",
        back_populates="license",
        cascade="all, delete-orphan",
    )


class RegisteredDevice(Base):
    """
    Registered device allowed to use a COSMOS license.
    """

    __tablename__ = "registered_devices"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    license_id: Mapped[int] = mapped_column(
        ForeignKey("licenses.id"),
        nullable=False,
    )

    machine_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )

    device_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    operating_system: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    connector_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    license = relationship(
        "License",
        back_populates="devices",
    )
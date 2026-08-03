"""
===============================================================================
COSMOS Core Configuration

Centralized configuration for the COSMOS Trading Operating System.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application configuration."""

    APP_NAME: str = "COSMOS"

    APP_VERSION: str = "1.0.0-alpha"

    DEBUG: bool = True

    THEME: str = "dark"

    AI_NAME: str = "COSMOS AI"

    DEFAULT_SYMBOL: str = "EURUSD"

    DEFAULT_TIMEFRAME: str = "M15"

    DATABASE_URL: str = "sqlite:///cosmos.db"
 
settings = Settings()
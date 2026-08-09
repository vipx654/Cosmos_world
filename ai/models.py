"""
===============================================================================
COSMOS AI Models

Core AI models shared across every intelligent agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================


class TrendDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    SIDEWAYS = "SIDEWAYS"
    UNKNOWN = "UNKNOWN"


class SwingType(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


class MarketPhase(str, Enum):
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    REVERSAL = "REVERSAL"
    ACCUMULATION = "ACCUMULATION"
    DISTRIBUTION = "DISTRIBUTION"


class SignalStrength(str, Enum):
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


# =============================================================================
# MARKET DATA
# =============================================================================


@dataclass(slots=True)
class MarketCandle:
    """
    Single OHLCV candle.
    """

    timestamp: datetime

    open: float
    high: float
    low: float
    close: float

    volume: float


# =============================================================================
# SWING
# =============================================================================


@dataclass(slots=True)
class SwingPoint:
    """
    Swing High / Swing Low.
    """

    index: int

    price: float

    timestamp: datetime

    swing_type: SwingType


# =============================================================================
# TREND ANALYSIS
# =============================================================================


@dataclass(slots=True)
class TrendAnalysis:
    """
    Output of Trend Agent.
    """

    direction: TrendDirection

    confidence: float

    strength: float

    structure: str

    structures: list[str]

    acceleration: bool

    momentum: float

    reasons: list[str] = field(default_factory=list)


# =============================================================================
# AGENT RESULT
# =============================================================================


@dataclass(slots=True)
class AgentResult:
    """
    Base response object returned by every AI agent.
    """

    name: str

    confidence: float

    success: bool

    analysis: object

    execution_time_ms: float = 0.0
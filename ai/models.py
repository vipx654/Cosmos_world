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
# CHART ANNOTATION
# =============================================================================


class AnnotationType(str, Enum):
    """
    Universal visual event types produced by COSMOS agents.

    These values form the contract between the AI layer and
    the future COSMOS chart/UI layer.
    """

    # -------------------------------------------------------------------------
    # Trend
    # -------------------------------------------------------------------------

    SWING_HIGH = "SWING_HIGH"
    SWING_LOW = "SWING_LOW"

    HIGHER_HIGH = "HIGHER_HIGH"
    HIGHER_LOW = "HIGHER_LOW"

    LOWER_HIGH = "LOWER_HIGH"
    LOWER_LOW = "LOWER_LOW"

    BULLISH_TRENDLINE = "BULLISH_TRENDLINE"
    BEARISH_TRENDLINE = "BEARISH_TRENDLINE"

    SUPPORT = "SUPPORT"
    RESISTANCE = "RESISTANCE"

    # -------------------------------------------------------------------------
    # Market Structure
    # -------------------------------------------------------------------------

    BOS_BULLISH = "BOS_BULLISH"
    BOS_BEARISH = "BOS_BEARISH"

    CHOCH_BULLISH = "CHOCH_BULLISH"
    CHOCH_BEARISH = "CHOCH_BEARISH"

    MSS_BULLISH = "MSS_BULLISH"
    MSS_BEARISH = "MSS_BEARISH"

    # -------------------------------------------------------------------------
    # Price Events
    # -------------------------------------------------------------------------

    BREAKOUT_BULLISH = "BREAKOUT_BULLISH"
    BREAKOUT_BEARISH = "BREAKOUT_BEARISH"

    # -------------------------------------------------------------------------
    # Generic
    # -------------------------------------------------------------------------

    LEVEL = "LEVEL"
    MARKER = "MARKER"
    REGION = "REGION"


class AnnotationDirection(str, Enum):
    """
    Direction associated with a chart annotation.
    """

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


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
# CHART ANNOTATION MODEL
# =============================================================================


@dataclass(slots=True)
class ChartAnnotation:
    """
    Universal visual representation of an AI analysis event.

    Every intelligent agent can publish ChartAnnotation objects.
    The chart/UI layer can then render these objects without knowing
    how the underlying analysis was calculated.

    An annotation can represent:

        - swing points
        - HH / HL / LH / LL
        - trendlines
        - support / resistance
        - BOS
        - CHOCH
        - MSS
        - breakouts
        - future SMC / liquidity events
    """

    # -------------------------------------------------------------------------
    # Identity
    # -------------------------------------------------------------------------

    id: str

    agent: str

    annotation_type: AnnotationType

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

    label: str = ""

    direction: AnnotationDirection = (
        AnnotationDirection.NEUTRAL
    )

    # -------------------------------------------------------------------------
    # Chart Coordinates
    # -------------------------------------------------------------------------
    #
    # start_index / end_index allow lines and regions.
    # start_price / end_price allow horizontal/diagonal price objects.
    #
    # For a point annotation, only start_index/start_price may be required.
    # -------------------------------------------------------------------------

    start_index: int | None = None

    end_index: int | None = None

    start_price: float | None = None

    end_price: float | None = None

    # -------------------------------------------------------------------------
    # Analysis Metadata
    # -------------------------------------------------------------------------

    confidence: float = 0.0

    locked: bool = False

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    # -------------------------------------------------------------------------
    # Additional Agent Data
    # -------------------------------------------------------------------------

    metadata: dict[str, object] = field(
        default_factory=dict
    )


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
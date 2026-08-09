"""
===============================================================================
COSMOS Order Block Models

Institutional Order Block data models.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================


class OrderBlockType(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    BREAKER = "BREAKER"
    UNKNOWN = "UNKNOWN"


class OrderBlockStatus(str, Enum):
    FRESH = "FRESH"
    TESTED = "TESTED"
    MITIGATED = "MITIGATED"
    INVALID = "INVALID"


class OrderBlockDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class MitigationStatus(str, Enum):
    UNTOUCHED = "UNTOUCHED"
    PARTIAL = "PARTIAL"
    FULL = "FULL"
    INVALIDATED = "INVALIDATED"


# =============================================================================
# ORDER BLOCK
# =============================================================================


@dataclass(slots=True)
class OrderBlock:
    """
    Represents one detected order block.
    """

    block_type: OrderBlockType

    status: OrderBlockStatus

    direction: OrderBlockDirection

    high: float

    low: float

    candle_index: int

    confidence: float

    probability: float

    strength: float

    mitigation_status: MitigationStatus = (
        MitigationStatus.UNTOUCHED
    )

    mitigation_count: int = 0

    breaker: bool = False

    valid: bool = True

    timeframe: str = ""

    source: str = ""

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# MITIGATION RESULT
# =============================================================================


@dataclass(slots=True)
class MitigationResult:
    """
    Result of order block mitigation analysis.
    """

    order_block: OrderBlock

    status: MitigationStatus

    penetration: float

    touched: bool

    fully_mitigated: bool

    invalidated: bool

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# CONFIRMATION RESULT
# =============================================================================


@dataclass(slots=True)
class OrderBlockConfirmation:
    """
    Confirmation information for an order block.
    """

    order_block: OrderBlock

    confirmed: bool

    score: float

    reasons: list[str] = field(
        default_factory=list
    )


# =============================================================================
# ORDER BLOCK MAP
# =============================================================================


@dataclass(slots=True)
class OrderBlockMap:
    """
    Organized collection of detected order blocks.
    """

    bullish: list[OrderBlock]

    bearish: list[OrderBlock]

    breakers: list[OrderBlock]

    mitigated: list[OrderBlock]

    fresh: list[OrderBlock]

    tested: list[OrderBlock]

    invalid: list[OrderBlock]

    all_blocks: list[OrderBlock]


# =============================================================================
# FINAL ANALYSIS
# =============================================================================


@dataclass(slots=True)
class OrderBlockAnalysis:
    """
    Final Order Block Agent analysis.
    """

    direction: OrderBlockDirection

    confidence: float

    probability: float

    order_block_map: OrderBlockMap

    reasons: list[str]

    strongest_block: OrderBlock | None = None

    strongest_bullish: OrderBlock | None = None

    strongest_bearish: OrderBlock | None = None

    confirmed_blocks: list[OrderBlock] = field(
        default_factory=list
    )
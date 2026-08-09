"""
===============================================================================
COSMOS Sweep Models

Institutional Sweep Models

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


class SweepType(str, Enum):

    BUY_SIDE = "BUY_SIDE"

    SELL_SIDE = "SELL_SIDE"

    INTERNAL = "INTERNAL"

    EXTERNAL = "EXTERNAL"

    UNKNOWN = "UNKNOWN"


class SweepStatus(str, Enum):

    PENDING = "PENDING"

    CONFIRMED = "CONFIRMED"

    FAILED = "FAILED"

    INVALID = "INVALID"


class SweepDirection(str, Enum):

    BULLISH = "BULLISH"

    BEARISH = "BEARISH"

    NEUTRAL = "NEUTRAL"


# =============================================================================
# SWEEP OBJECT
# =============================================================================


@dataclass(slots=True)
class SweepObject:
    """
    Represents one detected liquidity sweep.
    """

    sweep_type: SweepType

    status: SweepStatus

    direction: SweepDirection

    price: float

    candle_index: int

    confidence: float

    probability: float

    strength: float

    fake: bool = False

    session: str = ""

    source: str = ""

    evidence: list[str] = field(default_factory=list)


# =============================================================================
# SWEEP MAP
# =============================================================================


@dataclass(slots=True)
class SweepMap:
    """
    Stores every sweep detected by the agent.
    """

    buy_side: list[SweepObject]

    sell_side: list[SweepObject]

    fake_sweeps: list[SweepObject]

    confirmed: list[SweepObject]

    all_sweeps: list[SweepObject]


# =============================================================================
# FINAL ANALYSIS
# =============================================================================


@dataclass(slots=True)
class SweepAnalysis:
    """
    Final Sweep Agent analysis.
    """

    direction: SweepDirection

    confidence: float

    probability: float

    sweep_map: SweepMap

    reasons: list[str]
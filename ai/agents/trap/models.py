"""
===============================================================================
COSMOS Trap Agent Models

Data models shared by the Trap Agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# =============================================================================
# ENUMS
# =============================================================================


class TrapDirection(str, Enum):
    """Direction of the failed breakout."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class TrapType(str, Enum):
    """Type of trap detected."""

    BULL_TRAP = "bull_trap"
    BEAR_TRAP = "bear_trap"
    NONE = "none"


class TrapState(str, Enum):
    """Current state of the trap setup."""

    NONE = "none"
    BREAKOUT = "breakout"
    REJECTION = "rejection"
    RECLAIMED = "reclaimed"
    CONFIRMED = "confirmed"


# =============================================================================
# BREAKOUT MODEL
# =============================================================================


@dataclass
class BreakoutEvent:
    """
    Represents a meaningful move beyond a reference liquidity/structure level.
    """

    detected: bool = False

    direction: TrapDirection = (
        TrapDirection.NEUTRAL
    )

    level: float = 0.0

    breakout_price: float = 0.0

    extension: float = 0.0

    extension_ratio: float = 0.0

    candle_index: int = -1

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# RECLAIM MODEL
# =============================================================================


@dataclass
class ReclaimEvent:
    """
    Represents price returning back across the broken level.
    """

    detected: bool = False

    direction: TrapDirection = (
        TrapDirection.NEUTRAL
    )

    level: float = 0.0

    reclaim_price: float = 0.0

    bars_after_breakout: int = 0

    strength: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# REJECTION MODEL
# =============================================================================


@dataclass
class RejectionEvent:
    """
    Represents rejection of the breakout area.
    """

    detected: bool = False

    direction: TrapDirection = (
        TrapDirection.NEUTRAL
    )

    wick_ratio: float = 0.0

    body_ratio: float = 0.0

    close_position: float = 0.0

    strength: float = 0.0

    candle_index: int = -1

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# VOLUME MODEL
# =============================================================================


@dataclass
class TrapVolumeEvidence:
    """
    Volume/activity evidence associated with a potential trap.
    """

    available: bool = False

    relative_volume: float = 0.0

    elevated: bool = False

    strong: bool = False

    direction: TrapDirection = (
        TrapDirection.NEUTRAL
    )

    strength: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# FOLLOW-THROUGH MODEL
# =============================================================================


@dataclass
class FollowThroughFailure:
    """
    Represents failure of price to continue after the breakout.
    """

    detected: bool = False

    direction: TrapDirection = (
        TrapDirection.NEUTRAL
    )

    bars_observed: int = 0

    continuation_distance: float = 0.0

    failure_strength: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# TRAP CANDIDATE
# =============================================================================


@dataclass
class TrapCandidate:
    """
    Intermediate representation produced after combining the individual
    trap-detection components.
    """

    detected: bool = False

    trap_type: TrapType = (
        TrapType.NONE
    )

    direction: TrapDirection = (
        TrapDirection.NEUTRAL
    )

    state: TrapState = (
        TrapState.NONE
    )

    level: float = 0.0

    score: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )

    breakout: BreakoutEvent | None = None

    reclaim: ReclaimEvent | None = None

    rejection: RejectionEvent | None = None

    volume: TrapVolumeEvidence | None = None

    follow_through: FollowThroughFailure | None = None


# =============================================================================
# PROBABILITY MODEL
# =============================================================================


@dataclass
class TrapProbability:
    """
    Directional probability generated from trap evidence.

    This is evidence weighting, NOT a guaranteed probability of profit.
    """

    direction: TrapDirection = (
        TrapDirection.NEUTRAL
    )

    trap_type: TrapType = (
        TrapType.NONE
    )

    bullish_probability: float = 50.0

    bearish_probability: float = 50.0

    neutral_probability: float = 50.0

    confidence: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# FINAL TRAP RESULT
# =============================================================================


@dataclass
class TrapResult:
    """
    Final result exposed by the Trap Agent.
    """

    detected: bool = False

    trap_type: TrapType = (
        TrapType.NONE
    )

    direction: TrapDirection = (
        TrapDirection.NEUTRAL
    )

    state: TrapState = (
        TrapState.NONE
    )

    level: float = 0.0

    probability: float = 50.0

    confidence: float = 0.0

    score: float = 0.0

    valid: bool = False

    evidence: list[str] = field(
        default_factory=list
    )

    breakout: BreakoutEvent | None = None

    reclaim: ReclaimEvent | None = None

    rejection: RejectionEvent | None = None

    volume: TrapVolumeEvidence | None = None

    follow_through: FollowThroughFailure | None = None

    probability_analysis: TrapProbability | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
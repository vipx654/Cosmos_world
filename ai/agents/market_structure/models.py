"""
===============================================================================
COSMOS Market Structure Models

Institutional market structure data models.

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


class StructureBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class StructureEventType(str, Enum):
    BOS = "BOS"
    CHOCH = "CHOCH"
    MSS = "MSS"


class StructureDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class StructureLevelType(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


# =============================================================================
# STRUCTURE LEVEL
# =============================================================================


@dataclass(slots=True)
class StructureLevel:
    """
    Represents an important structural price level.

    Used for protected highs/lows and structural break validation.
    """

    level_type: StructureLevelType

    price: float

    index: int

    strength: float = 0.0

    protected: bool = False


# =============================================================================
# STRUCTURE EVENT
# =============================================================================


@dataclass(slots=True)
class StructureEvent:
    """
    Represents a validated institutional structure event.
    """

    event_type: StructureEventType

    direction: StructureDirection

    broken_price: float

    swing_index: int

    confidence: float

    confirmed: bool = True

    displacement: float = 0.0

    strength: float = 0.0

    reasons: list[str] = field(
        default_factory=list,
    )


# =============================================================================
# RAW STRUCTURE
# =============================================================================


@dataclass(slots=True)
class StructureAnalysis:
    """
    Raw market structure before BOS / CHOCH / MSS analysis.
    """

    higher_highs: int

    higher_lows: int

    lower_highs: int

    lower_lows: int

    bias: StructureBias

    protected_high: StructureLevel | None = None

    protected_low: StructureLevel | None = None

    strength: float = 0.0

    confidence: float = 0.0


# =============================================================================
# BOS ANALYSIS
# =============================================================================


@dataclass(slots=True)
class BOSAnalysis:
    """
    Break Of Structure analysis.

    Retains the original public fields while exposing
    richer structural metadata.
    """

    bullish: bool

    bearish: bool

    broken_price: float | None

    confidence: float

    event: StructureEvent | None = None

    reasons: list[str] = field(
        default_factory=list,
    )


# =============================================================================
# CHOCH ANALYSIS
# =============================================================================


@dataclass(slots=True)
class CHOCHAnalysis:
    """
    Change Of Character analysis.

    Represents the first validated structural warning
    against the prevailing structure.
    """

    detected: bool

    bullish: bool

    bearish: bool

    confidence: float

    event: StructureEvent | None = None

    reasons: list[str] = field(
        default_factory=list,
    )


# =============================================================================
# MSS ANALYSIS
# =============================================================================


@dataclass(slots=True)
class MSSAnalysis:
    """
    Market Structure Shift analysis.

    MSS is kept separate from CHOCH so downstream
    strategy agents can distinguish the events.
    """

    detected: bool

    bullish: bool

    bearish: bool

    confidence: float

    event: StructureEvent | None = None

    reasons: list[str] = field(
        default_factory=list,
    )


# =============================================================================
# INTERNAL STRUCTURE
# =============================================================================


@dataclass(slots=True)
class InternalStructureAnalysis:
    """
    Internal market structure.
    """

    bias: StructureBias

    strength: float

    confidence: float

    event: StructureEvent | None = None

    reasons: list[str] = field(
        default_factory=list,
    )


# =============================================================================
# EXTERNAL STRUCTURE
# =============================================================================


@dataclass(slots=True)
class ExternalStructureAnalysis:
    """
    Dominant external market structure.
    """

    bias: StructureBias

    strength: float

    confidence: float

    protected_high: StructureLevel | None = None

    protected_low: StructureLevel | None = None

    reasons: list[str] = field(
        default_factory=list,
    )


# =============================================================================
# FINAL MARKET STRUCTURE ANALYSIS
# =============================================================================


@dataclass(slots=True)
class MarketStructureAnalysis:
    """
    Final output of the Market Structure Agent.

    Original compatibility fields are preserved.
    """

    bullish_bos: bool

    bearish_bos: bool

    choch: bool

    mss: bool

    internal_bias: StructureBias

    external_bias: StructureBias

    confidence: float

    reasons: list[str]

    # -------------------------------------------------------------------------
    # v2 structural metadata
    # -------------------------------------------------------------------------

    bos_event: StructureEvent | None = None

    choch_event: StructureEvent | None = None

    mss_event: StructureEvent | None = None

    protected_high: StructureLevel | None = None

    protected_low: StructureLevel | None = None

    structure_strength: float = 0.0

    conflict: bool = False

    conflict_reason: str | None = None
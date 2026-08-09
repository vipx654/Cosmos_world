"""
===============================================================================
COSMOS Fair Value Gap Models

Data models for FVG detection, mitigation, inversion, confirmation,
probability, confidence, mapping and final analysis.

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


class FVGType(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    INVERSION = "INVERSION"
    UNKNOWN = "UNKNOWN"


class FVGStatus(str, Enum):
    FRESH = "FRESH"
    TESTED = "TESTED"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    INVALID = "INVALID"


class FVGDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class MitigationStatus(str, Enum):
    UNTOUCHED = "UNTOUCHED"
    PARTIAL = "PARTIAL"
    FULL = "FULL"
    INVALIDATED = "INVALIDATED"


class InversionStatus(str, Enum):
    NONE = "NONE"
    POTENTIAL = "POTENTIAL"
    CONFIRMED = "CONFIRMED"


# =============================================================================
# FAIR VALUE GAP
# =============================================================================


@dataclass(slots=True)
class FairValueGap:
    """
    Represents one detected Fair Value Gap.

    For a bullish FVG:

        gap_low  = first candle high
        gap_high = third candle low

    For a bearish FVG:

        gap_high = first candle low
        gap_low  = third candle high
    """

    fvg_type: FVGType

    status: FVGStatus

    direction: FVGDirection

    high: float

    low: float

    first_candle_index: int

    middle_candle_index: int

    third_candle_index: int

    confidence: float

    probability: float

    strength: float

    midpoint: float

    mitigation_status: MitigationStatus = (
        MitigationStatus.UNTOUCHED
    )

    mitigation_count: int = 0

    fill_ratio: float = 0.0

    inverted: bool = False

    inversion_status: InversionStatus = (
        InversionStatus.NONE
    )

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
class FVGMitigationResult:
    """
    Result of FVG mitigation analysis.
    """

    fvg: FairValueGap

    status: MitigationStatus

    fill_ratio: float

    touched: bool

    partially_filled: bool

    fully_filled: bool

    invalidated: bool

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# INVERSION RESULT
# =============================================================================


@dataclass(slots=True)
class FVGInversionResult:
    """
    Result of FVG inversion analysis.
    """

    fvg: FairValueGap

    status: InversionStatus

    inverted: bool

    new_direction: FVGDirection

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# CONFIRMATION RESULT
# =============================================================================


@dataclass(slots=True)
class FVGConfirmation:
    """
    Confirmation result for an FVG.
    """

    fvg: FairValueGap

    confirmed: bool

    score: float

    reasons: list[str] = field(
        default_factory=list
    )


# =============================================================================
# FVG MAP
# =============================================================================


@dataclass(slots=True)
class FVGMap:
    """
    Organized collection of detected Fair Value Gaps.
    """

    bullish: list[FairValueGap]

    bearish: list[FairValueGap]

    inverted: list[FairValueGap]

    mitigated: list[FairValueGap]

    fresh: list[FairValueGap]

    tested: list[FairValueGap]

    partial: list[FairValueGap]

    filled: list[FairValueGap]

    invalid: list[FairValueGap]

    all_fvgs: list[FairValueGap]


# =============================================================================
# FINAL ANALYSIS
# =============================================================================


@dataclass(slots=True)
class FVGAnalysis:
    """
    Final FVG Agent analysis.
    """

    direction: FVGDirection

    confidence: float

    probability: float

    fvg_map: FVGMap

    reasons: list[str]

    strongest_fvg: FairValueGap | None = None

    strongest_bullish: FairValueGap | None = None

    strongest_bearish: FairValueGap | None = None

    confirmed_fvgs: list[FairValueGap] = field(
        default_factory=list
    )
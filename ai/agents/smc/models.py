"""
===============================================================================
COSMOS Smart Money Concept Models

Institutional data models for Smart Money Concept analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================


class ZoneType(str, Enum):
    PREMIUM = "PREMIUM"
    DISCOUNT = "DISCOUNT"
    EQUILIBRIUM = "EQUILIBRIUM"


class FVGType(str, Enum):
    NONE = "NONE"
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class FVGStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    INVALID = "INVALID"


class InducementType(str, Enum):
    NONE = "NONE"
    BUY_SIDE = "BUY_SIDE"
    SELL_SIDE = "SELL_SIDE"


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass(slots=True)
class DealingRange:

    high: float

    low: float

    equilibrium: float


@dataclass(slots=True)
class PremiumDiscount:

    zone: ZoneType

    distance_from_eq: float


@dataclass(slots=True)
class FairValueGap:

    gap_type: FVGType

    status: FVGStatus

    upper: float

    lower: float


@dataclass(slots=True)
class EqualLevel:

    price: float

    touches: int


@dataclass(slots=True)
class Inducement:

    inducement_type: InducementType

    price: float

    confidence: float


@dataclass(slots=True)
class SMCAnalysis:

    dealing_range: DealingRange

    premium_discount: PremiumDiscount

    fvg: FairValueGap

    equal_high: EqualLevel | None

    equal_low: EqualLevel | None

    inducement: Inducement

    confidence: float

    reasons: list[str]
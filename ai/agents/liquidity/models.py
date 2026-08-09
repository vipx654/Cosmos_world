"""
===============================================================================
COSMOS Liquidity Models

Institutional liquidity models.

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


class LiquidityType(str, Enum):

    BUY_SIDE = "BUY_SIDE"

    SELL_SIDE = "SELL_SIDE"

    INTERNAL = "INTERNAL"

    EXTERNAL = "EXTERNAL"


class LiquidityStatus(str, Enum):

    UNTOUCHED = "UNTOUCHED"

    SWEPT = "SWEPT"

    PARTIAL = "PARTIAL"


# =============================================================================
# LIQUIDITY OBJECT
# =============================================================================


@dataclass(slots=True)
class LiquidityObject:
    """
    Represents one liquidity level.
    """

    liquidity_type: LiquidityType

    status: LiquidityStatus

    price: float

    touches: int

    strength: float

    confidence: float

    quality: float = 0.0

    age: int = 0

    distance: float = 0.0

    source: str = ""

    evidence: list[str] = field(default_factory=list)


# =============================================================================
# LIQUIDITY CLUSTER
# =============================================================================


@dataclass(slots=True)
class LiquidityCluster:
    """
    Institutional liquidity pool.
    """

    id: str

    center_price: float

    upper_price: float

    lower_price: float

    liquidity_count: int

    combined_strength: float

    combined_confidence: float

    expected_sweep_probability: float

    members: list[LiquidityObject] = field(default_factory=list)


# =============================================================================
# LIQUIDITY MAP
# =============================================================================


@dataclass(slots=True)
class LiquidityMap:
    """
    Complete market liquidity map.
    """

    buy_side: list[LiquidityObject]

    sell_side: list[LiquidityObject]

    internal: list[LiquidityObject]

    external: list[LiquidityObject]

    clusters: list[LiquidityCluster]

    all_levels: list[LiquidityObject]


# =============================================================================
# FINAL ANALYSIS
# =============================================================================


@dataclass(slots=True)
class LiquidityAnalysis:
    """
    Final liquidity analysis returned by the agent.
    """

    liquidity_map: LiquidityMap

    confidence: float

    reasons: list[str]
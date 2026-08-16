"""
===============================================================================
COSMOS Liquidity Models

Institutional liquidity models.

Author: COSMOS Development Team
License: MIT
Version: 2.0.0
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


class LiquidityRole(str, Enum):
    """
    Functional role of a liquidity level.
    """

    TARGET = "TARGET"

    INDUCEMENT = "INDUCEMENT"

    MAGNET = "MAGNET"

    PROTECTION = "PROTECTION"

    REFERENCE = "REFERENCE"

    UNKNOWN = "UNKNOWN"


class LiquidityQuality(str, Enum):
    """
    Qualitative classification of liquidity quality.
    """

    LOW = "LOW"

    MODERATE = "MODERATE"

    HIGH = "HIGH"

    EXTREME = "EXTREME"


class LiquidityFreshness(str, Enum):
    """
    Freshness state of a liquidity level.
    """

    FRESH = "FRESH"

    ACTIVE = "ACTIVE"

    AGING = "AGING"

    STALE = "STALE"


class SweepProbability(str, Enum):
    """
    Qualitative sweep probability classification.
    """

    VERY_LOW = "VERY_LOW"

    LOW = "LOW"

    MODERATE = "MODERATE"

    HIGH = "HIGH"

    VERY_HIGH = "VERY_HIGH"


# =============================================================================
# LIQUIDITY OBJECT
# =============================================================================


@dataclass(slots=True)
class LiquidityObject:
    """
    Represents one institutional liquidity level.

    This object contains both detection information and downstream
    decision-support information for Sweep, Decision, Risk, and Chart agents.
    """

    # -------------------------------------------------------------------------
    # Core Identity
    # -------------------------------------------------------------------------

    liquidity_type: LiquidityType

    status: LiquidityStatus

    price: float

    # -------------------------------------------------------------------------
    # Detection
    # -------------------------------------------------------------------------

    touches: int

    strength: float

    confidence: float

    quality: float = 0.0

    # -------------------------------------------------------------------------
    # Market Context
    # -------------------------------------------------------------------------

    age: int = 0

    distance: float = 0.0

    source: str = ""

    timeframe: str = ""

    symbol: str = ""

    # -------------------------------------------------------------------------
    # Institutional Classification
    # -------------------------------------------------------------------------

    role: LiquidityRole = LiquidityRole.UNKNOWN

    quality_class: LiquidityQuality = (
        LiquidityQuality.LOW
    )

    freshness: LiquidityFreshness = (
        LiquidityFreshness.FRESH
    )

    # -------------------------------------------------------------------------
    # Sweep Intelligence
    # -------------------------------------------------------------------------

    sweep_probability: float = 0.0

    sweep_class: SweepProbability = (
        SweepProbability.VERY_LOW
    )

    sweep_count: int = 0

    last_swept_age: int | None = None

    # -------------------------------------------------------------------------
    # Mitigation
    # -------------------------------------------------------------------------

    mitigation: float = 0.0

    mitigation_count: int = 0

    # -------------------------------------------------------------------------
    # Confluence
    # -------------------------------------------------------------------------

    confluence_score: float = 0.0

    confluence_factors: list[str] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # Ranking
    # -------------------------------------------------------------------------

    priority: float = 0.0

    target_score: float = 0.0

    # -------------------------------------------------------------------------
    # Evidence
    # -------------------------------------------------------------------------

    evidence: list[str] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # Source References
    # -------------------------------------------------------------------------

    source_indices: list[int] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # Chart Integration
    # -------------------------------------------------------------------------

    chart_id: str = ""

    annotation_id: str = ""

    locked: bool = False

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    metadata: dict[str, object] = field(
        default_factory=dict
    )


# =============================================================================
# LIQUIDITY CLUSTER
# =============================================================================


@dataclass(slots=True)
class LiquidityCluster:
    """
    Institutional liquidity pool.

    A cluster represents multiple nearby liquidity levels that may
    collectively act as a stronger target or sweep zone.
    """

    # -------------------------------------------------------------------------
    # Identity
    # -------------------------------------------------------------------------

    id: str

    # -------------------------------------------------------------------------
    # Price Range
    # -------------------------------------------------------------------------

    center_price: float

    upper_price: float

    lower_price: float

    # -------------------------------------------------------------------------
    # Composition
    # -------------------------------------------------------------------------

    liquidity_count: int

    combined_strength: float

    combined_confidence: float

    # -------------------------------------------------------------------------
    # Sweep Intelligence
    # -------------------------------------------------------------------------

    expected_sweep_probability: float

    sweep_class: SweepProbability = (
        SweepProbability.VERY_LOW
    )

    # -------------------------------------------------------------------------
    # Institutional Classification
    # -------------------------------------------------------------------------

    role: LiquidityRole = LiquidityRole.UNKNOWN

    quality: float = 0.0

    priority: float = 0.0

    # -------------------------------------------------------------------------
    # Confluence
    # -------------------------------------------------------------------------

    confluence_score: float = 0.0

    confluence_factors: list[str] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # Members
    # -------------------------------------------------------------------------

    members: list[LiquidityObject] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # Chart Integration
    # -------------------------------------------------------------------------

    annotation_id: str = ""

    locked: bool = False

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    metadata: dict[str, object] = field(
        default_factory=dict
    )


# =============================================================================
# LIQUIDITY MAP
# =============================================================================


@dataclass(slots=True)
class LiquidityMap:
    """
    Complete institutional liquidity map.

    This is the primary structured representation consumed by
    downstream agents and the COSMOS chart/UI layer.
    """

    # -------------------------------------------------------------------------
    # Liquidity Categories
    # -------------------------------------------------------------------------

    buy_side: list[LiquidityObject]

    sell_side: list[LiquidityObject]

    internal: list[LiquidityObject]

    external: list[LiquidityObject]

    # -------------------------------------------------------------------------
    # Clusters
    # -------------------------------------------------------------------------

    clusters: list[LiquidityCluster]

    # -------------------------------------------------------------------------
    # Unified Levels
    # -------------------------------------------------------------------------

    all_levels: list[LiquidityObject]

    # -------------------------------------------------------------------------
    # Ranked Liquidity
    # -------------------------------------------------------------------------

    nearest_targets: list[LiquidityObject] = field(
        default_factory=list
    )

    strongest_levels: list[LiquidityObject] = field(
        default_factory=list
    )

    sweep_candidates: list[LiquidityObject] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # Map Statistics
    # -------------------------------------------------------------------------

    total_levels: int = 0

    total_clusters: int = 0

    buy_side_count: int = 0

    sell_side_count: int = 0

    internal_count: int = 0

    external_count: int = 0

    # -------------------------------------------------------------------------
    # Global Intelligence
    # -------------------------------------------------------------------------

    dominant_type: LiquidityType | None = None

    strongest_price: float | None = None

    nearest_price: float | None = None

    # -------------------------------------------------------------------------
    # Chart Integration
    # -------------------------------------------------------------------------

    annotation_ids: list[str] = field(
        default_factory=list
    )

    locked: bool = False

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    metadata: dict[str, object] = field(
        default_factory=dict
    )


# =============================================================================
# FINAL ANALYSIS
# =============================================================================


@dataclass(slots=True)
class LiquidityAnalysis:
    """
    Final liquidity analysis returned by the Liquidity Agent.

    Contains the complete institutional liquidity map together with
    directional intelligence, sweep intelligence, decision support,
    explainability, and chart integration state.
    """

    # -------------------------------------------------------------------------
    # Primary Analysis
    # -------------------------------------------------------------------------

    liquidity_map: LiquidityMap

    confidence: float

    # -------------------------------------------------------------------------
    # Directional Intelligence
    # -------------------------------------------------------------------------

    bullish_score: float = 0.0

    bearish_score: float = 0.0

    directional_bias: str = "NEUTRAL"

    # -------------------------------------------------------------------------
    # Sweep Intelligence
    # -------------------------------------------------------------------------

    highest_sweep_probability: float = 0.0

    primary_sweep_target: LiquidityObject | None = None

    primary_cluster: LiquidityCluster | None = None

    # -------------------------------------------------------------------------
    # Decision Support
    # -------------------------------------------------------------------------

    target_count: int = 0

    high_quality_count: int = 0

    fresh_count: int = 0

    swept_count: int = 0

    # -------------------------------------------------------------------------
    # Explainability
    # -------------------------------------------------------------------------

    reasons: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    evidence: list[str] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # Chart Integration
    # -------------------------------------------------------------------------

    annotation_ids: list[str] = field(
        default_factory=list
    )

    locked: bool = False

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    metadata: dict[str, object] = field(
        default_factory=dict
    )
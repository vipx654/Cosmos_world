"""
===============================================================================
COSMOS Fair Value Gap Models V3

Production-grade data contracts for the COSMOS Fair Value Gap Agent.

Responsibilities:
    - Represent detected Fair Value Gaps
    - Represent lifecycle / mitigation state
    - Represent inversion state
    - Represent confirmation state
    - Represent confluence state
    - Represent ranking state
    - Represent visualization mapping
    - Represent final FVG analysis

Design principles:
    - Data-only contracts
    - No detection logic
    - No scoring algorithms
    - No trading execution logic
    - Backward-compatible core fields
    - Explicit state for downstream COSMOS agents
    - Safe bounded-score representation
    - Visualization-ready metadata

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


class FVGDecision(str, Enum):
    """
    High-level decision state produced from finalized FVG intelligence.

    This is NOT an order/execution instruction.
    """

    NONE = "NONE"
    WATCH = "WATCH"
    VALID = "VALID"
    HIGH_CONFLUENCE = "HIGH_CONFLUENCE"
    AVOID = "AVOID"


class FVGQuality(str, Enum):
    """
    Human-readable quality classification.
    """

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    EXTREME = "EXTREME"


class FVGVisualizationState(str, Enum):
    """
    Rendering state consumed by the visualization layer.
    """

    ACTIVE = "ACTIVE"
    MITIGATED = "MITIGATED"
    FILLED = "FILLED"
    INVALID = "INVALID"
    INVERTED = "INVERTED"
    HIDDEN = "HIDDEN"


# =============================================================================
# VISUALIZATION MAP
# =============================================================================


@dataclass(slots=True)
class FVGVisualization:
    """
    Visualization metadata for one FVG.

    The model does not render anything.

    The chart/UI layer consumes this mapping to determine:
        - where the FVG is
        - which direction it represents
        - whether it remains active
        - whether it has inverted
        - what label should be displayed
    """

    key: str = ""

    label: str = ""

    state: FVGVisualizationState = (
        FVGVisualizationState.ACTIVE
    )

    direction: FVGDirection = (
        FVGDirection.NEUTRAL
    )

    high: float = 0.0

    low: float = 0.0

    midpoint: float = 0.0

    active: bool = True

    inverted: bool = False

    timeframe: str = ""

    source: str = ""


# =============================================================================
# CONFLUENCE STATE
# =============================================================================


@dataclass(slots=True)
class FVGConfluence:
    """
    Structured confluence state.

    Individual COSMOS agents can populate these values later.

    Scores are expected to be normalized to 0-100.
    """

    trend: float = 0.0

    market_structure: float = 0.0

    liquidity: float = 0.0

    sweep: float = 0.0

    order_block: float = 0.0

    smc: float = 0.0

    volume: float = 0.0

    session: float = 0.0

    htf: float = 0.0

    displacement: float = 0.0

    score: float = 0.0

    conflict_penalty: float = 0.0

    reasons: list[str] = field(
        default_factory=list
    )


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
        gap_low = third candle high

    The model stores state.

    Detection, mitigation, inversion, scoring and confirmation remain in
    their dedicated engines.
    """

    # -------------------------------------------------------------------------
    # Core identity
    # -------------------------------------------------------------------------

    fvg_type: FVGType

    status: FVGStatus

    direction: FVGDirection

    # -------------------------------------------------------------------------
    # Price boundaries
    # -------------------------------------------------------------------------

    high: float

    low: float

    midpoint: float

    # -------------------------------------------------------------------------
    # Formation indices
    # -------------------------------------------------------------------------

    first_candle_index: int

    middle_candle_index: int

    third_candle_index: int

    # -------------------------------------------------------------------------
    # Core scores
    # -------------------------------------------------------------------------

    confidence: float

    probability: float

    strength: float

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    timeframe: str = ""

    source: str = ""

    evidence: list[str] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # V3 quality / confluence / ranking
    # -------------------------------------------------------------------------

    quality_score: float = 0.0

    confluence_score: float = 0.0

    ranking_score: float = 0.0

    quality: FVGQuality = (
        FVGQuality.MODERATE
    )

    decision: FVGDecision = (
        FVGDecision.NONE
    )

    # -------------------------------------------------------------------------
    # Structured confluence
    # -------------------------------------------------------------------------

    confluence: FVGConfluence = field(
        default_factory=FVGConfluence
    )

    # -------------------------------------------------------------------------
    # Confirmation
    # -------------------------------------------------------------------------

    confirmed: bool = False

    confirmation_score: float = 0.0

    confirmation_reasons: list[str] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # Visualization
    # -------------------------------------------------------------------------

    visualization: FVGVisualization = field(
        default_factory=FVGVisualization
    )

    # -------------------------------------------------------------------------
    # Lifecycle metadata
    # -------------------------------------------------------------------------

    age: int = 0

    last_interaction_index: int | None = None

    first_touch_index: int | None = None

    filled_index: int | None = None

    invalidated_index: int | None = None

    inverted_index: int | None = None


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

    This is the primary mapping contract between the FVG engine and
    downstream consumers such as:
        - dashboard
        - chart renderer
        - strategy engine
        - prediction engine
        - risk engine
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

    # -------------------------------------------------------------------------
    # V3 convenience collections
    # -------------------------------------------------------------------------

    confirmed: list[FairValueGap] = field(
        default_factory=list
    )

    active: list[FairValueGap] = field(
        default_factory=list
    )

    high_quality: list[FairValueGap] = field(
        default_factory=list
    )

    high_confluence: list[FairValueGap] = field(
        default_factory=list
    )


# =============================================================================
# FINAL ANALYSIS
# =============================================================================


@dataclass(slots=True)
class FVGAnalysis:
    """
    Final FVG Agent analysis.

    This is the stable output contract consumed by higher-level COSMOS
    systems.
    """

    # -------------------------------------------------------------------------
    # Directional output
    # -------------------------------------------------------------------------

    direction: FVGDirection

    # -------------------------------------------------------------------------
    # Aggregate scores
    # -------------------------------------------------------------------------

    confidence: float

    probability: float

    confluence_score: float = 0.0

    ranking_score: float = 0.0

    # -------------------------------------------------------------------------
    # Decision
    # -------------------------------------------------------------------------

    decision: FVGDecision = (
        FVGDecision.NONE
    )

    # -------------------------------------------------------------------------
    # FVG map
    # -------------------------------------------------------------------------

    fvg_map: FVGMap | None = None

    # -------------------------------------------------------------------------
    # Explanation
    # -------------------------------------------------------------------------

    reasons: list[str] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # Strongest structures
    # -------------------------------------------------------------------------

    strongest_fvg: FairValueGap | None = None

    strongest_bullish: FairValueGap | None = None

    strongest_bearish: FairValueGap | None = None

    # -------------------------------------------------------------------------
    # Confirmation
    # -------------------------------------------------------------------------

    confirmed_fvgs: list[FairValueGap] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # V3 aggregate counts
    # -------------------------------------------------------------------------

    total_fvgs: int = 0

    bullish_count: int = 0

    bearish_count: int = 0

    inverted_count: int = 0

    mitigated_count: int = 0

    active_count: int = 0

    confirmed_count: int = 0

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    engine_version: str = ""

    timeframe: str = ""

    source: str = ""
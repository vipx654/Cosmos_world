"""
===============================================================================
COSMOS Fair Value Gap Utilities V3

Shared, deterministic utility layer for the COSMOS FVG agent.

Responsibilities
----------------
- Candle measurements and validation
- FVG geometry calculations
- Price/FVG interaction
- Direction-aware mitigation measurement
- FVG lifecycle classification
- Safe FVG state mutation
- Inversion helpers
- Score aggregation
- Ranking helpers
- Directional filtering
- Lifecycle filtering
- Evidence helpers
- Numeric safety / bounded scoring

Design principles
-----------------
- No orchestration logic
- No dependency on other FVG engines
- Deterministic calculations
- Defensive numeric handling
- Direction-aware calculations
- Bounded score handling
- No mutation unless explicitly requested
- Safe operation with lightweight test fixtures
- Suitable for future multi-agent confluence

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from typing import Any

from ai.agents.fvg.constants import (
    EPSILON,
    FULL_FILL_RATIO,
    MAX_CONFIDENCE,
    MAX_PROBABILITY,
    MAX_SCORE,
    MAX_STRENGTH,
    MIN_CONFIDENCE,
    MIN_PROBABILITY,
    MIN_SCORE,
    MIN_STRENGTH,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGDirection,
    FVGStatus,
    InversionStatus,
    MitigationStatus,
)


# =============================================================================
# NUMERIC SAFETY
# =============================================================================


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Convert a value to a finite float.

    Non-numeric, NaN and infinite values are replaced with ``default``.
    """

    try:
        result = float(value)
    except (TypeError, ValueError):
        return float(default)

    if not math.isfinite(result):
        return float(default)

    return result


def clamp(
    value: float,
    minimum: float = MIN_SCORE,
    maximum: float = MAX_SCORE,
) -> float:
    """
    Clamp a numeric value into a bounded range.
    """

    value = safe_float(value, minimum)

    if minimum > maximum:
        minimum, maximum = maximum, minimum

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def clamp_score(value: float) -> float:
    """
    Clamp a generic COSMOS score to 0-100.
    """

    return clamp(
        value,
        MIN_SCORE,
        MAX_SCORE,
    )


def clamp_confidence(value: float) -> float:
    """
    Clamp confidence to the configured confidence range.
    """

    return clamp(
        value,
        MIN_CONFIDENCE,
        MAX_CONFIDENCE,
    )


def clamp_probability(value: float) -> float:
    """
    Clamp probability to the configured probability range.
    """

    return clamp(
        value,
        MIN_PROBABILITY,
        MAX_PROBABILITY,
    )


def clamp_strength(value: float) -> float:
    """
    Clamp strength to the configured strength range.
    """

    return clamp(
        value,
        MIN_STRENGTH,
        MAX_STRENGTH,
    )


def is_finite_number(value: Any) -> bool:
    """
    Return True when ``value`` can be represented as a finite float.
    """

    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


# =============================================================================
# CANDLE ACCESS
# =============================================================================


def candle_high(candle: Any) -> float:
    """
    Safely return candle high.
    """

    return safe_float(
        getattr(candle, "high", 0.0)
    )


def candle_low(candle: Any) -> float:
    """
    Safely return candle low.
    """

    return safe_float(
        getattr(candle, "low", 0.0)
    )


def candle_open(candle: Any) -> float:
    """
    Safely return candle open.
    """

    return safe_float(
        getattr(candle, "open", 0.0)
    )


def candle_close(candle: Any) -> float:
    """
    Safely return candle close.
    """

    return safe_float(
        getattr(candle, "close", 0.0)
    )


# =============================================================================
# CANDLE HELPERS
# =============================================================================


def candle_range(
    candle: Any,
) -> float:
    """
    Return the full candle range.

    Invalid negative ranges are normalized to zero.
    """

    return max(
        0.0,
        candle_high(candle)
        - candle_low(candle),
    )


def candle_body(
    candle: Any,
) -> float:
    """
    Return absolute candle body size.
    """

    return abs(
        candle_close(candle)
        - candle_open(candle)
    )


def body_ratio(
    candle: Any,
) -> float:
    """
    Return candle body / candle range.

    Result is bounded to 0-1.
    """

    total_range = candle_range(candle)

    if total_range <= EPSILON:
        return 0.0

    return clamp(
        candle_body(candle) / total_range,
        0.0,
        1.0,
    )


def upper_wick(
    candle: Any,
) -> float:
    """
    Return upper wick size.
    """

    high = candle_high(candle)
    open_price = candle_open(candle)
    close_price = candle_close(candle)

    return max(
        0.0,
        high - max(
            open_price,
            close_price,
        ),
    )


def lower_wick(
    candle: Any,
) -> float:
    """
    Return lower wick size.
    """

    low = candle_low(candle)
    open_price = candle_open(candle)
    close_price = candle_close(candle)

    return max(
        0.0,
        min(
            open_price,
            close_price,
        ) - low,
    )


def is_bullish_candle(
    candle: Any,
) -> bool:
    """
    Return True when candle closes above its open.
    """

    return (
        candle_close(candle)
        >
        candle_open(candle)
    )


def is_bearish_candle(
    candle: Any,
) -> bool:
    """
    Return True when candle closes below its open.
    """

    return (
        candle_close(candle)
        <
        candle_open(candle)
    )


def is_neutral_candle(
    candle: Any,
) -> bool:
    """
    Return True when candle open and close are equal.
    """

    return (
        abs(
            candle_close(candle)
            - candle_open(candle)
        )
        <= EPSILON
    )


# =============================================================================
# GAP HELPERS
# =============================================================================


def gap_range(
    fvg: FairValueGap,
) -> float:
    """
    Return absolute FVG price range.
    """

    return max(
        0.0,
        safe_float(fvg.high)
        - safe_float(fvg.low),
    )


def gap_midpoint(
    fvg: FairValueGap,
) -> float:
    """
    Calculate the midpoint of an FVG.
    """

    return calculate_midpoint(
        fvg.low,
        fvg.high,
    )


def calculate_midpoint(
    low: float,
    high: float,
) -> float:
    """
    Calculate the 50% midpoint of a price interval.
    """

    low = safe_float(low)
    high = safe_float(high)

    return (
        low + high
    ) / 2.0


def gap_is_valid(
    fvg: FairValueGap,
) -> bool:
    """
    Return whether an FVG has valid geometry.
    """

    low = safe_float(fvg.low)
    high = safe_float(fvg.high)

    return (
        math.isfinite(low)
        and math.isfinite(high)
        and high > low
    )


def gap_contains_price(
    fvg: FairValueGap,
    price: float,
) -> bool:
    """
    Return True when price is inside the FVG boundaries.
    """

    if not gap_is_valid(fvg):
        return False

    price = safe_float(price)

    return (
        fvg.low
        <= price
        <= fvg.high
    )


def price_inside_fvg(
    price: float,
    fvg: FairValueGap,
) -> bool:
    """
    Backward-compatible alias for gap_contains_price().
    """

    return gap_contains_price(
        fvg,
        price,
    )


def candle_touches_fvg(
    candle: Any,
    fvg: FairValueGap,
) -> bool:
    """
    Return True when the candle range intersects the FVG.
    """

    if not gap_is_valid(fvg):
        return False

    return (
        candle_high(candle)
        >= safe_float(fvg.low)
        and
        candle_low(candle)
        <= safe_float(fvg.high)
    )


def gap_overlap_ratio(
    candle: Any,
    fvg: FairValueGap,
) -> float:
    """
    Calculate geometric overlap between candle and FVG.

    Returns a value between 0 and 1.
    """

    total_gap = gap_range(fvg)

    if total_gap <= EPSILON:
        return 0.0

    overlap_low = max(
        candle_low(candle),
        safe_float(fvg.low),
    )

    overlap_high = min(
        candle_high(candle),
        safe_float(fvg.high),
    )

    if overlap_high <= overlap_low:
        return 0.0

    return clamp(
        (
            overlap_high
            - overlap_low
        )
        / total_gap,
        0.0,
        1.0,
    )


# =============================================================================
# DIRECTION HELPERS
# =============================================================================


def opposite_direction(
    direction: FVGDirection,
) -> FVGDirection:
    """
    Return the opposite FVG direction.
    """

    if direction == FVGDirection.BULLISH:
        return FVGDirection.BEARISH

    if direction == FVGDirection.BEARISH:
        return FVGDirection.BULLISH

    return FVGDirection.NEUTRAL


def direction_sign(
    direction: FVGDirection,
) -> int:
    """
    Convert FVG direction to a numerical sign.

    Bullish  -> +1
    Bearish  -> -1
    Neutral  -> 0
    """

    if direction == FVGDirection.BULLISH:
        return 1

    if direction == FVGDirection.BEARISH:
        return -1

    return 0


def direction_from_sign(
    sign: int,
) -> FVGDirection:
    """
    Convert a numerical direction sign into FVGDirection.
    """

    if sign > 0:
        return FVGDirection.BULLISH

    if sign < 0:
        return FVGDirection.BEARISH

    return FVGDirection.NEUTRAL


# =============================================================================
# FILL / MITIGATION
# =============================================================================


def calculate_fill_ratio(
    candle: Any,
    fvg: FairValueGap,
) -> float:
    """
    Calculate direction-aware FVG fill ratio.

    Bullish FVG:
        Price enters from the upper boundary.

    Bearish FVG:
        Price enters from the lower boundary.

    Returns:
        0.0 -> untouched
        0.5 -> midpoint filled
        1.0 -> fully filled
    """

    total_gap = gap_range(fvg)

    if total_gap <= EPSILON:
        return 0.0

    candle_high_value = candle_high(candle)
    candle_low_value = candle_low(candle)

    gap_high = safe_float(fvg.high)
    gap_low = safe_float(fvg.low)

    # No overlap.
    if (
        candle_high_value < gap_low
        or
        candle_low_value > gap_high
    ):
        return 0.0

    if fvg.direction == FVGDirection.BULLISH:

        penetration = (
            gap_high
            -
            max(
                gap_low,
                candle_low_value,
            )
        )

    elif fvg.direction == FVGDirection.BEARISH:

        penetration = (
            min(
                gap_high,
                candle_high_value,
            )
            -
            gap_low
        )

    else:
        return gap_overlap_ratio(
            candle,
            fvg,
        )

    return clamp(
        penetration / total_gap,
        0.0,
        1.0,
    )


def classify_fill(
    fill_ratio: float,
) -> MitigationStatus:
    """
    Convert normalized fill ratio to mitigation status.
    """

    fill_ratio = clamp(
        fill_ratio,
        0.0,
        1.0,
    )

    if fill_ratio <= EPSILON:
        return MitigationStatus.UNTOUCHED

    if fill_ratio < FULL_FILL_RATIO:
        return MitigationStatus.PARTIAL

    return MitigationStatus.FULL


def apply_fill_to_fvg(
    fvg: FairValueGap,
    fill_ratio: float,
) -> None:
    """
    Apply a new fill observation to an FVG.

    Fill ratio is monotonic: historical maximum fill is retained.
    """

    fill_ratio = clamp(
        fill_ratio,
        0.0,
        1.0,
    )

    previous_ratio = clamp(
        fvg.fill_ratio,
        0.0,
        1.0,
    )

    fvg.fill_ratio = max(
        previous_ratio,
        fill_ratio,
    )

    status = classify_fill(
        fvg.fill_ratio
    )

    fvg.mitigation_status = status

    if status == MitigationStatus.UNTOUCHED:
        fvg.status = FVGStatus.FRESH

    elif status == MitigationStatus.PARTIAL:
        fvg.status = FVGStatus.PARTIAL

    elif status == MitigationStatus.FULL:
        fvg.status = FVGStatus.FILLED


def mitigation_depth(
    fvg: FairValueGap,
) -> float:
    """
    Return current normalized mitigation depth.
    """

    return clamp(
        fvg.fill_ratio,
        0.0,
        1.0,
    )


def is_mitigated(
    fvg: FairValueGap,
) -> bool:
    """
    Return True when an FVG has received any mitigation.
    """

    return (
        fvg.mitigation_status
        != MitigationStatus.UNTOUCHED
    )


def is_fully_mitigated(
    fvg: FairValueGap,
) -> bool:
    """
    Return True when an FVG is fully filled.
    """

    return (
        fvg.mitigation_status
        == MitigationStatus.FULL
        or
        fvg.status
        == FVGStatus.FILLED
    )


# =============================================================================
# INVERSION
# =============================================================================


def is_inverted(
    fvg: FairValueGap,
) -> bool:
    """
    Return whether the FVG has become a confirmed inversion.
    """

    return (
        bool(fvg.inverted)
        or
        fvg.inversion_status
        == InversionStatus.CONFIRMED
    )


def is_potentially_inverted(
    fvg: FairValueGap,
) -> bool:
    """
    Return whether an FVG is in potential inversion state.
    """

    return (
        fvg.inversion_status
        == InversionStatus.POTENTIAL
    )


def active_direction(
    fvg: FairValueGap,
) -> FVGDirection:
    """
    Return the FVG's current active trading direction.

    Confirmed inversion reverses the original direction.
    """

    if is_inverted(fvg):
        return opposite_direction(
            fvg.direction
        )

    return fvg.direction


# =============================================================================
# SCORE AGGREGATION
# =============================================================================


def average_score(
    values: Iterable[float],
    default: float = 0.0,
) -> float:
    """
    Calculate a safe rounded average of numeric values.
    """

    values = [
        safe_float(value)
        for value in values
    ]

    if not values:
        return round(
            safe_float(default),
            2,
        )

    return round(
        sum(values) / len(values),
        2,
    )


def weighted_average(
    values: Iterable[tuple[float, float]],
    default: float = 0.0,
) -> float:
    """
    Calculate a deterministic weighted average.

    Each item is:
        (value, weight)
    """

    pairs = [
        (
            safe_float(value),
            max(
                0.0,
                safe_float(weight),
            ),
        )
        for value, weight in values
    ]

    total_weight = sum(
        weight
        for _, weight in pairs
    )

    if total_weight <= EPSILON:
        return round(
            safe_float(default),
            2,
        )

    return round(
        sum(
            value * weight
            for value, weight in pairs
        )
        / total_weight,
        2,
    )


def average_probability(
    fvgs: Sequence[FairValueGap],
) -> float:
    """
    Calculate average FVG probability.
    """

    return clamp_probability(
        average_score(
            (
                fvg.probability
                for fvg in fvgs
            )
        )
    )


def average_confidence(
    fvgs: Sequence[FairValueGap],
) -> float:
    """
    Calculate average FVG confidence.
    """

    return clamp_confidence(
        average_score(
            (
                fvg.confidence
                for fvg in fvgs
            )
        )
    )


def average_strength(
    fvgs: Sequence[FairValueGap],
) -> float:
    """
    Calculate average FVG strength.
    """

    return clamp_strength(
        average_score(
            (
                fvg.strength
                for fvg in fvgs
            )
        )
    )


# =============================================================================
# RANKING
# =============================================================================


def strongest_fvg(
    fvgs: Sequence[FairValueGap],
) -> FairValueGap | None:
    """
    Return the strongest FVG.

    Tie-breaking:
        strength
        confidence
        probability
        freshness
    """

    if not fvgs:
        return None

    return max(
        fvgs,
        key=lambda fvg: (
            clamp_strength(fvg.strength),
            clamp_confidence(fvg.confidence),
            clamp_probability(fvg.probability),
            -safe_float(
                fvg.fill_ratio
            ),
        ),
    )


def highest_confidence_fvg(
    fvgs: Sequence[FairValueGap],
) -> FairValueGap | None:
    """
    Return the FVG with highest confidence.
    """

    if not fvgs:
        return None

    return max(
        fvgs,
        key=lambda fvg: (
            clamp_confidence(
                fvg.confidence
            ),
            clamp_probability(
                fvg.probability
            ),
            clamp_strength(
                fvg.strength
            ),
        ),
    )


def highest_probability_fvg(
    fvgs: Sequence[FairValueGap],
) -> FairValueGap | None:
    """
    Return the FVG with highest probability.
    """

    if not fvgs:
        return None

    return max(
        fvgs,
        key=lambda fvg: (
            clamp_probability(
                fvg.probability
            ),
            clamp_confidence(
                fvg.confidence
            ),
            clamp_strength(
                fvg.strength
            ),
        ),
    )


def rank_fvgs(
    fvgs: Sequence[FairValueGap],
) -> list[FairValueGap]:
    """
    Return FVGs ranked from strongest to weakest.

    The original list is never modified.
    """

    return sorted(
        fvgs,
        key=lambda fvg: (
            clamp_strength(fvg.strength),
            clamp_confidence(fvg.confidence),
            clamp_probability(fvg.probability),
            -safe_float(
                fvg.fill_ratio
            ),
        ),
        reverse=True,
    )


# =============================================================================
# DIRECTIONAL FILTERS
# =============================================================================


def filter_bullish(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return bullish FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if active_direction(fvg)
        == FVGDirection.BULLISH
    ]


def filter_bearish(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return bearish FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if active_direction(fvg)
        == FVGDirection.BEARISH
    ]


def filter_neutral(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return neutral FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if active_direction(fvg)
        == FVGDirection.NEUTRAL
    ]


# =============================================================================
# LIFECYCLE FILTERS
# =============================================================================


def filter_fresh(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return fresh FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if fvg.status == FVGStatus.FRESH
    ]


def filter_tested(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return tested FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if fvg.status == FVGStatus.TESTED
    ]


def filter_partial(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return partially mitigated FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if (
            fvg.status == FVGStatus.PARTIAL
            or
            fvg.mitigation_status
            == MitigationStatus.PARTIAL
        )
    ]


def filter_filled(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return fully filled FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if is_fully_mitigated(fvg)
    ]


def filter_invalid(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return invalid FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if (
            fvg.status == FVGStatus.INVALID
            or
            not fvg.valid
            or
            fvg.mitigation_status
            == MitigationStatus.INVALIDATED
        )
    ]


# =============================================================================
# INVERSION FILTERS
# =============================================================================


def filter_inverted(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return confirmed inverted FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if is_inverted(fvg)
    ]


def filter_potential_inversions(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return FVGs in potential inversion state.
    """

    return [
        fvg
        for fvg in fvgs
        if is_potentially_inverted(fvg)
    ]


# =============================================================================
# CONFIRMATION / ACTIONABILITY FILTERS
# =============================================================================


def filter_valid(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Return geometrically and logically valid FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if fvg.valid
        and fvg.status != FVGStatus.INVALID
        and gap_is_valid(fvg)
    ]


def filter_confirmed(
    fvgs: Iterable[FairValueGap],
    minimum_confidence: float = 0.0,
    minimum_probability: float = 0.0,
) -> list[FairValueGap]:
    """
    Return FVGs meeting configurable confidence/probability requirements.
    """

    minimum_confidence = clamp_confidence(
        minimum_confidence
    )

    minimum_probability = clamp_probability(
        minimum_probability
    )

    return [
        fvg
        for fvg in fvgs
        if (
            fvg.valid
            and
            fvg.status != FVGStatus.INVALID
            and
            clamp_confidence(
                fvg.confidence
            )
            >= minimum_confidence
            and
            clamp_probability(
                fvg.probability
            )
            >= minimum_probability
        )
    ]


# =============================================================================
# EVIDENCE
# =============================================================================


def add_evidence(
    fvg: FairValueGap,
    evidence: str,
) -> None:
    """
    Add unique evidence to an FVG.

    Empty evidence is ignored.
    """

    evidence = str(
        evidence
    ).strip()

    if not evidence:
        return

    if evidence not in fvg.evidence:
        fvg.evidence.append(
            evidence
        )


def merge_evidence(
    fvg: FairValueGap,
    evidence: Iterable[str],
) -> None:
    """
    Add multiple unique evidence entries.
    """

    for item in evidence:
        add_evidence(
            fvg,
            item,
        )


def evidence_count(
    fvg: FairValueGap,
) -> int:
    """
    Return number of unique evidence entries.
    """

    return len(
        fvg.evidence
    )


# =============================================================================
# COLLECTION HELPERS
# =============================================================================


def deduplicate_fvgs(
    fvgs: Iterable[FairValueGap],
) -> list[FairValueGap]:
    """
    Remove duplicate FVGs using their candle-index identity and geometry.

    The first occurrence is retained.
    """

    result: list[FairValueGap] = []
    seen: set[tuple[Any, ...]] = set()

    for fvg in fvgs:

        key = (
            fvg.first_candle_index,
            fvg.middle_candle_index,
            fvg.third_candle_index,
            fvg.direction,
            round(
                safe_float(fvg.low),
                12,
            ),
            round(
                safe_float(fvg.high),
                12,
            ),
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(fvg)

    return result


def limit_fvgs(
    fvgs: Iterable[FairValueGap],
    maximum: int,
) -> list[FairValueGap]:
    """
    Return at most ``maximum`` FVGs.

    Existing order is preserved.
    """

    maximum = max(
        0,
        int(maximum),
    )

    if maximum == 0:
        return []

    return list(fvgs)[:maximum]
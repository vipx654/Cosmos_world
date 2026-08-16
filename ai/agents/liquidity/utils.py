"""
===============================================================================
COSMOS Liquidity Utilities

Advanced Institutional Liquidity Utility Layer.

Responsibilities:
    • Liquidity quality statistics
    • Strength statistics
    • Confidence statistics
    • Directional filtering
    • Status filtering
    • Type filtering
    • Strongest / weakest liquidity
    • Liquidity ranking
    • Weighted quality
    • Touch statistics
    • Age statistics
    • Distance statistics
    • Evidence statistics
    • Liquidity distribution
    • Safe numeric normalization
    • Deterministic helper functions

These utilities are intentionally stateless and reusable by:

    LiquidityEngine
    MapEngine
    QualityEngine
    ClusterEngine
    SweepEngine
    Future decision agents

Author: COSMOS Development Team
License: MIT
Version: 2.0.0
===============================================================================
"""

from __future__ import annotations

from collections import Counter

from ai.agents.liquidity.models import (
    LiquidityObject,
    LiquidityStatus,
    LiquidityType,
)


# =============================================================================
# BASIC QUALITY
# =============================================================================


def average_quality(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Return average liquidity quality.
    """

    if not liquidity:
        return 0.0

    values = [
        _bounded(level.quality)
        for level in liquidity
        if level is not None
    ]

    if not values:
        return 0.0

    return round(
        sum(values)
        / len(values),
        2,
    )


def strongest_liquidity(
    liquidity: list[LiquidityObject],
) -> LiquidityObject | None:
    """
    Return the highest-quality liquidity level.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return None

    return max(
        valid,
        key=lambda level: (
            _bounded(level.quality),
            _bounded(level.strength),
            int(level.touches),
        ),
    )


def weakest_liquidity(
    liquidity: list[LiquidityObject],
) -> LiquidityObject | None:
    """
    Return the lowest-quality liquidity level.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return None

    return min(
        valid,
        key=lambda level: (
            _bounded(level.quality),
            _bounded(level.strength),
            int(level.touches),
        ),
    )


# =============================================================================
# STRENGTH
# =============================================================================


def average_strength(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Calculate average liquidity strength.
    """

    values = [
        _bounded(level.strength)
        for level in liquidity
        if level is not None
    ]

    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        2,
    )


def strongest_by_strength(
    liquidity: list[LiquidityObject],
) -> LiquidityObject | None:
    """
    Return the liquidity level with the greatest raw strength.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return None

    return max(
        valid,
        key=lambda level: (
            _bounded(level.strength),
            _bounded(level.quality),
        ),
    )


# =============================================================================
# CONFIDENCE
# =============================================================================


def average_confidence(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Calculate average detection confidence.
    """

    values = [
        _bounded(level.confidence)
        for level in liquidity
        if level is not None
    ]

    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        2,
    )


def highest_confidence(
    liquidity: list[LiquidityObject],
) -> LiquidityObject | None:
    """
    Return the highest-confidence liquidity level.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return None

    return max(
        valid,
        key=lambda level: (
            _bounded(level.confidence),
            _bounded(level.quality),
        ),
    )


# =============================================================================
# TOUCHES
# =============================================================================


def total_touches(
    liquidity: list[LiquidityObject],
) -> int:
    """
    Return total observed liquidity touches.
    """

    return sum(
        max(
            int(level.touches),
            0,
        )
        for level in liquidity
        if level is not None
    )


def average_touches(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Return average number of touches.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return 0.0

    return round(
        total_touches(valid)
        / len(valid),
        2,
    )


def most_touched(
    liquidity: list[LiquidityObject],
) -> LiquidityObject | None:
    """
    Return the most frequently touched liquidity level.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return None

    return max(
        valid,
        key=lambda level: (
            max(
                int(level.touches),
                0,
            ),
            _bounded(level.quality),
        ),
    )


# =============================================================================
# AGE
# =============================================================================


def average_age(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Calculate average liquidity age.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return 0.0

    return round(
        sum(
            max(
                int(level.age),
                0,
            )
            for level in valid
        )
        / len(valid),
        2,
    )


def freshest_liquidity(
    liquidity: list[LiquidityObject],
) -> LiquidityObject | None:
    """
    Return the freshest liquidity level.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return None

    return min(
        valid,
        key=lambda level: max(
            int(level.age),
            0,
        ),
    )


# =============================================================================
# DISTANCE
# =============================================================================


def closest_liquidity(
    liquidity: list[LiquidityObject],
) -> LiquidityObject | None:
    """
    Return liquidity closest to the reference price/distance supplied
    by upstream analysis.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return None

    return min(
        valid,
        key=lambda level: abs(
            float(level.distance)
        ),
    )


def average_distance(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Calculate average liquidity distance.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return 0.0

    return round(
        sum(
            abs(
                float(level.distance)
            )
            for level in valid
        )
        / len(valid),
        10,
    )


# =============================================================================
# FILTERING
# =============================================================================


def filter_by_type(
    liquidity: list[LiquidityObject],
    liquidity_type: LiquidityType,
) -> list[LiquidityObject]:
    """
    Return liquidity matching one liquidity type.
    """

    return [
        level
        for level in liquidity
        if level is not None
        and level.liquidity_type == liquidity_type
    ]


def filter_by_status(
    liquidity: list[LiquidityObject],
    status: LiquidityStatus,
) -> list[LiquidityObject]:
    """
    Return liquidity matching one status.
    """

    return [
        level
        for level in liquidity
        if level is not None
        and level.status == status
    ]


def untouched_liquidity(
    liquidity: list[LiquidityObject],
) -> list[LiquidityObject]:
    """
    Return untouched liquidity.
    """

    return filter_by_status(
        liquidity,
        LiquidityStatus.UNTOUCHED,
    )


def swept_liquidity(
    liquidity: list[LiquidityObject],
) -> list[LiquidityObject]:
    """
    Return fully swept liquidity.
    """

    return filter_by_status(
        liquidity,
        LiquidityStatus.SWEPT,
    )


def partial_liquidity(
    liquidity: list[LiquidityObject],
) -> list[LiquidityObject]:
    """
    Return partially consumed liquidity.
    """

    return filter_by_status(
        liquidity,
        LiquidityStatus.PARTIAL,
    )


# =============================================================================
# QUALITY FILTERING
# =============================================================================


def high_quality_liquidity(
    liquidity: list[LiquidityObject],
    threshold: float = 70.0,
) -> list[LiquidityObject]:
    """
    Return liquidity whose quality meets the supplied threshold.
    """

    threshold = _bounded(
        threshold
    )

    return [
        level
        for level in liquidity
        if level is not None
        and _bounded(level.quality) >= threshold
    ]


def strong_liquidity(
    liquidity: list[LiquidityObject],
    threshold: float = 70.0,
) -> list[LiquidityObject]:
    """
    Return liquidity whose structural strength meets the threshold.
    """

    threshold = _bounded(
        threshold
    )

    return [
        level
        for level in liquidity
        if level is not None
        and _bounded(level.strength) >= threshold
    ]


# =============================================================================
# RANKING
# =============================================================================


def rank_liquidity(
    liquidity: list[LiquidityObject],
) -> list[LiquidityObject]:
    """
    Return liquidity ranked by institutional significance.

    Ranking priority:

        Quality
        Strength
        Confidence
        Touches
    """

    return sorted(
        (
            level
            for level in liquidity
            if level is not None
        ),
        key=lambda level: (
            _bounded(level.quality),
            _bounded(level.strength),
            _bounded(level.confidence),
            max(
                int(level.touches),
                0,
            ),
        ),
        reverse=True,
    )


# =============================================================================
# WEIGHTED QUALITY
# =============================================================================


def weighted_quality(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Calculate quality weighted by liquidity strength.

    Stronger liquidity contributes more to the final score.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return 0.0

    numerator = sum(
        _bounded(level.quality)
        * max(
            _bounded(level.strength),
            1.0,
        )
        for level in valid
    )

    denominator = sum(
        max(
            _bounded(level.strength),
            1.0,
        )
        for level in valid
    )

    if denominator <= 0:
        return 0.0

    return round(
        numerator / denominator,
        2,
    )


# =============================================================================
# DIRECTIONAL SUMMARY
# =============================================================================


def directional_summary(
    liquidity: list[LiquidityObject],
) -> dict[str, int]:
    """
    Return a count of major liquidity directions.
    """

    counts = {
        "buy_side": 0,
        "sell_side": 0,
        "internal": 0,
        "external": 0,
    }

    for level in liquidity:

        if level is None:
            continue

        if level.liquidity_type == LiquidityType.BUY_SIDE:
            counts["buy_side"] += 1

        elif level.liquidity_type == LiquidityType.SELL_SIDE:
            counts["sell_side"] += 1

        elif level.liquidity_type == LiquidityType.INTERNAL:
            counts["internal"] += 1

        elif level.liquidity_type == LiquidityType.EXTERNAL:
            counts["external"] += 1

    return counts


# =============================================================================
# STATUS SUMMARY
# =============================================================================


def status_summary(
    liquidity: list[LiquidityObject],
) -> dict[str, int]:
    """
    Return liquidity status distribution.
    """

    counts = {
        "untouched": 0,
        "partial": 0,
        "swept": 0,
    }

    for level in liquidity:

        if level is None:
            continue

        if level.status == LiquidityStatus.UNTOUCHED:
            counts["untouched"] += 1

        elif level.status == LiquidityStatus.PARTIAL:
            counts["partial"] += 1

        elif level.status == LiquidityStatus.SWEPT:
            counts["swept"] += 1

    return counts


# =============================================================================
# SOURCE SUMMARY
# =============================================================================


def source_summary(
    liquidity: list[LiquidityObject],
) -> dict[str, int]:
    """
    Count liquidity by detection source.
    """

    counter: Counter[str] = Counter()

    for level in liquidity:

        if level is None:
            continue

        source = (
            str(
                level.source
            ).strip()
            or "unknown"
        )

        counter[source] += 1

    return dict(
        counter
    )


# =============================================================================
# EVIDENCE
# =============================================================================


def total_evidence(
    liquidity: list[LiquidityObject],
) -> int:
    """
    Return total number of evidence records.
    """

    return sum(
        len(level.evidence)
        for level in liquidity
        if level is not None
    )


def average_evidence(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Return average evidence count per liquidity level.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return 0.0

    return round(
        total_evidence(valid)
        / len(valid),
        2,
    )


# =============================================================================
# DISTRIBUTION
# =============================================================================


def price_range(
    liquidity: list[LiquidityObject],
) -> tuple[float, float] | None:
    """
    Return lowest and highest liquidity price.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return None

    prices = [
        float(level.price)
        for level in valid
    ]

    return (
        min(prices),
        max(prices),
    )


def price_span(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Return total price span covered by liquidity.
    """

    result = price_range(
        liquidity
    )

    if result is None:
        return 0.0

    lower, upper = result

    return abs(
        upper - lower
    )


# =============================================================================
# LIQUIDITY CONCENTRATION
# =============================================================================


def concentration_score(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Estimate how concentrated the liquidity map is.

    This is a structural concentration metric, not a trade signal.
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if len(valid) < 2:
        return 0.0

    span = price_span(
        valid
    )

    if span <= 0:
        return 100.0

    total_strength = sum(
        _bounded(level.strength)
        for level in valid
    )

    if total_strength <= 0:
        return 0.0

    # Higher liquidity density per unit of price span produces a higher
    # concentration score.
    density = (
        len(valid)
        / span
    )

    strength_factor = (
        total_strength
        / len(valid)
        / 100.0
    )

    score = (
        density
        * strength_factor
    )

    # Stable bounded transformation.
    normalized = (
        100.0
        * (
            score
            / (
                1.0
                + score
            )
        )
    )

    return round(
        max(
            0.0,
            min(
                normalized,
                100.0,
            ),
        ),
        2,
    )


# =============================================================================
# MARKET-SIDE BALANCE
# =============================================================================


def buy_sell_balance(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Calculate buy-side vs sell-side balance.

    Result:

        +100 → strongly buy-side
           0 → balanced
        -100 → strongly sell-side
    """

    buy = sum(
        _bounded(level.strength)
        for level in liquidity
        if level is not None
        and level.liquidity_type
        == LiquidityType.BUY_SIDE
    )

    sell = sum(
        _bounded(level.strength)
        for level in liquidity
        if level is not None
        and level.liquidity_type
        == LiquidityType.SELL_SIDE
    )

    total = (
        buy + sell
    )

    if total <= 0:
        return 0.0

    return round(
        (
            (
                buy - sell
            )
            / total
        )
        * 100.0,
        2,
    )


# =============================================================================
# INSTITUTIONAL SCORE
# =============================================================================


def institutional_score(
    liquidity: list[LiquidityObject],
) -> float:
    """
    Calculate an aggregate institutional liquidity score.

    Combines:

        Weighted Quality
        Average Strength
        Average Confidence
        Touch Density
        Evidence Density
        Concentration
    """

    valid = [
        level
        for level in liquidity
        if level is not None
    ]

    if not valid:
        return 0.0

    quality = weighted_quality(
        valid
    )

    strength = average_strength(
        valid
    )

    confidence = average_confidence(
        valid
    )

    touches = min(
        average_touches(valid)
        * 20.0,
        100.0,
    )

    evidence = min(
        average_evidence(valid)
        * 15.0,
        100.0,
    )

    concentration = concentration_score(
        valid
    )

    score = (
        quality * 0.30
        + strength * 0.20
        + confidence * 0.20
        + touches * 0.10
        + evidence * 0.10
        + concentration * 0.10
    )

    return round(
        max(
            0.0,
            min(
                score,
                100.0,
            ),
        ),
        2,
    )


# =============================================================================
# SAFE NUMERIC HELPER
# =============================================================================


def _bounded(
    value: float,
) -> float:
    """
    Safely clamp a numeric value to 0..100.
    """

    try:

        value = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0

    if value != value:
        return 0.0

    if value == float("inf"):
        return 100.0

    if value == float("-inf"):
        return 0.0

    return max(
        0.0,
        min(
            value,
            100.0,
        ),
    )
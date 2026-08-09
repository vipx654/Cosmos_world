"""
===============================================================================
COSMOS Fair Value Gap Utilities

Shared helper functions for FVG detection, measurement, mitigation and
filtering.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.constants import (
    FULL_FILL_RATIO,
    PARTIAL_FILL_RATIO,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGDirection,
    FVGStatus,
    FVGType,
    InversionStatus,
    MitigationStatus,
)


# =============================================================================
# CANDLE HELPERS
# =============================================================================


def candle_range(candle) -> float:
    """
    Return the full candle range.
    """

    return max(
        0.0,
        float(candle.high) - float(candle.low),
    )


def candle_body(candle) -> float:
    """
    Return the absolute candle body size.
    """

    return abs(
        float(candle.close)
        -
        float(candle.open)
    )


def body_ratio(candle) -> float:
    """
    Return candle body divided by candle range.

    Returns 0 when the candle has no range.
    """

    total_range = candle_range(candle)

    if total_range <= 0:
        return 0.0

    return candle_body(candle) / total_range


def is_bullish_candle(candle) -> bool:
    """
    Return True when candle closes above its open.
    """

    return (
        float(candle.close)
        >
        float(candle.open)
    )


def is_bearish_candle(candle) -> bool:
    """
    Return True when candle closes below its open.
    """

    return (
        float(candle.close)
        <
        float(candle.open)
    )


# =============================================================================
# GAP HELPERS
# =============================================================================


def gap_range(
    fvg: FairValueGap,
) -> float:
    """
    Return the absolute price range of an FVG.
    """

    return max(
        0.0,
        float(fvg.high)
        -
        float(fvg.low),
    )


def calculate_midpoint(
    low: float,
    high: float,
) -> float:
    """
    Calculate the 50% midpoint of an FVG.
    """

    return (
        float(low)
        +
        float(high)
    ) / 2.0


def price_inside_fvg(
    price: float,
    fvg: FairValueGap,
) -> bool:
    """
    Check whether price is currently inside an FVG.
    """

    return (
        float(fvg.low)
        <= float(price)
        <= float(fvg.high)
    )


def candle_touches_fvg(
    candle,
    fvg: FairValueGap,
) -> bool:
    """
    Check whether a candle range touches an FVG.
    """

    return (
        float(candle.high)
        >= float(fvg.low)
        and
        float(candle.low)
        <= float(fvg.high)
    )


# =============================================================================
# FILL / MITIGATION
# =============================================================================


def calculate_fill_ratio(
    candle,
    fvg: FairValueGap,
) -> float:
    """
    Calculate normalized FVG fill.

    0.0 = no fill
    1.0 = completely filled
    """

    total_gap = gap_range(fvg)

    if total_gap <= 0:
        return 0.0

    candle_high = float(candle.high)
    candle_low = float(candle.low)

    gap_high = float(fvg.high)
    gap_low = float(fvg.low)

    # No overlap.
    if (
        candle_high < gap_low
        or
        candle_low > gap_high
    ):
        return 0.0

    # -------------------------------------------------------------------------
    # Bullish FVG
    #
    # Price enters from the upper side.
    # -------------------------------------------------------------------------

    if fvg.direction == FVGDirection.BULLISH:

        penetration = (
            gap_high
            -
            max(
                gap_low,
                candle_low,
            )
        )

        return min(
            1.0,
            max(
                0.0,
                penetration / total_gap,
            ),
        )

    # -------------------------------------------------------------------------
    # Bearish FVG
    #
    # Price enters from the lower side.
    # -------------------------------------------------------------------------

    if fvg.direction == FVGDirection.BEARISH:

        penetration = (
            min(
                gap_high,
                candle_high,
            )
            -
            gap_low
        )

        return min(
            1.0,
            max(
                0.0,
                penetration / total_gap,
            ),
        )

    return 0.0


def classify_fill(
    fill_ratio: float,
) -> MitigationStatus:
    """
    Convert a normalized fill ratio into mitigation status.
    """

    fill_ratio = max(
        0.0,
        min(
            1.0,
            float(fill_ratio),
        ),
    )

    if fill_ratio <= 0.0:
        return MitigationStatus.UNTOUCHED

    if fill_ratio < FULL_FILL_RATIO:
        return MitigationStatus.PARTIAL

    return MitigationStatus.FULL


def apply_fill_to_fvg(
    fvg: FairValueGap,
    fill_ratio: float,
) -> None:
    """
    Update an FVG with the latest fill information.
    """

    fill_ratio = max(
        0.0,
        min(
            1.0,
            float(fill_ratio),
        ),
    )

    fvg.fill_ratio = max(
        fvg.fill_ratio,
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


# =============================================================================
# INVERSION
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


def is_inverted(
    fvg: FairValueGap,
) -> bool:
    """
    Return whether the FVG has become an inversion.
    """

    return (
        fvg.inverted
        or
        fvg.inversion_status
        == InversionStatus.CONFIRMED
    )


# =============================================================================
# QUALITY
# =============================================================================


def average_probability(
    fvgs: list[FairValueGap],
) -> float:
    """
    Calculate average FVG probability.
    """

    if not fvgs:
        return 0.0

    return round(
        sum(
            float(fvg.probability)
            for fvg in fvgs
        )
        /
        len(fvgs),
        2,
    )


def average_confidence(
    fvgs: list[FairValueGap],
) -> float:
    """
    Calculate average FVG confidence.
    """

    if not fvgs:
        return 0.0

    return round(
        sum(
            float(fvg.confidence)
            for fvg in fvgs
        )
        /
        len(fvgs),
        2,
    )


def strongest_fvg(
    fvgs: list[FairValueGap],
) -> FairValueGap | None:
    """
    Return the strongest FVG.
    """

    if not fvgs:
        return None

    return max(
        fvgs,
        key=lambda fvg: fvg.strength,
    )


def highest_confidence_fvg(
    fvgs: list[FairValueGap],
) -> FairValueGap | None:
    """
    Return the FVG with the highest confidence.
    """

    if not fvgs:
        return None

    return max(
        fvgs,
        key=lambda fvg: fvg.confidence,
    )


# =============================================================================
# FILTERS
# =============================================================================


def filter_bullish(
    fvgs: list[FairValueGap],
) -> list[FairValueGap]:
    """
    Return bullish FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if fvg.direction
        == FVGDirection.BULLISH
    ]


def filter_bearish(
    fvgs: list[FairValueGap],
) -> list[FairValueGap]:
    """
    Return bearish FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if fvg.direction
        == FVGDirection.BEARISH
    ]


def filter_fresh(
    fvgs: list[FairValueGap],
) -> list[FairValueGap]:
    """
    Return fresh FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if fvg.status
        == FVGStatus.FRESH
    ]


def filter_partial(
    fvgs: list[FairValueGap],
) -> list[FairValueGap]:
    """
    Return partially filled FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if fvg.status
        == FVGStatus.PARTIAL
    ]


def filter_filled(
    fvgs: list[FairValueGap],
) -> list[FairValueGap]:
    """
    Return fully filled FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if fvg.status
        == FVGStatus.FILLED
        or
        fvg.mitigation_status
        == MitigationStatus.FULL
    ]


def filter_inverted(
    fvgs: list[FairValueGap],
) -> list[FairValueGap]:
    """
    Return inverted FVGs.
    """

    return [
        fvg
        for fvg in fvgs
        if is_inverted(fvg)
    ]
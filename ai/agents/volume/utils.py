"""
===============================================================================
COSMOS Volume Agent Utilities

Shared calculations for volume analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from math import isnan

from ai.agents.volume.constants import (
    EXTREME_RELATIVE_VOLUME,
    HIGH_RELATIVE_VOLUME,
    LOW_RELATIVE_VOLUME,
    NORMAL_RELATIVE_VOLUME,
)

from ai.agents.volume.models import (
    VolumeDirection,
    VolumeState,
    VolumeType,
)


# =============================================================================
# BASIC VOLUME
# =============================================================================


def safe_float(value) -> float:
    """
    Safely convert a value to float.

    Returns 0.0 for None or invalid numeric values.
    """

    if value is None:
        return 0.0

    try:
        result = float(value)

    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    if isnan(result):
        return 0.0

    return result


def candle_volume(candle) -> float:
    """
    Return candle volume as a float.
    """

    return max(
        0.0,
        safe_float(
            getattr(
                candle,
                "volume",
                0.0,
            )
        ),
    )


def average_volume(
    candles,
) -> float:
    """
    Calculate simple average volume.
    """

    if not candles:
        return 0.0

    volumes = [
        candle_volume(candle)
        for candle in candles
    ]

    if not volumes:
        return 0.0

    return sum(volumes) / len(volumes)


def relative_volume(
    volume: float,
    average: float,
) -> float:
    """
    Calculate Relative Volume.

        RVOL = current volume / average volume

    Returns 0 when average volume is unavailable.
    """

    volume = max(
        0.0,
        safe_float(volume),
    )

    average = max(
        0.0,
        safe_float(average),
    )

    if average <= 0.0:
        return 0.0

    return volume / average


# =============================================================================
# VOLUME STATE
# =============================================================================


def classify_volume(
    relative: float,
) -> VolumeState:
    """
    Classify relative volume into a normalized state.
    """

    relative = max(
        0.0,
        safe_float(relative),
    )

    if relative < LOW_RELATIVE_VOLUME:

        return VolumeState.VERY_LOW

    if relative < NORMAL_RELATIVE_VOLUME:

        return VolumeState.LOW

    if relative < HIGH_RELATIVE_VOLUME:

        return VolumeState.NORMAL

    if relative < EXTREME_RELATIVE_VOLUME:

        return VolumeState.HIGH

    return VolumeState.EXTREME


def volume_state_score(
    state: VolumeState,
) -> float:
    """
    Convert volume state into a 0-100 activity score.
    """

    scores = {
        VolumeState.VERY_LOW: 10.0,
        VolumeState.LOW: 30.0,
        VolumeState.NORMAL: 50.0,
        VolumeState.HIGH: 75.0,
        VolumeState.EXTREME: 100.0,
    }

    return scores.get(
        state,
        50.0,
    )


# =============================================================================
# PRICE
# =============================================================================


def price_change(
    candle,
) -> float:
    """
    Return absolute candle price change.
    """

    return (
        safe_float(
            getattr(
                candle,
                "close",
                0.0,
            )
        )
        -
        safe_float(
            getattr(
                candle,
                "open",
                0.0,
            )
        )
    )


def price_change_percent(
    candle,
) -> float:
    """
    Return candle price change percentage.
    """

    open_price = safe_float(
        getattr(
            candle,
            "open",
            0.0,
        )
    )

    close_price = safe_float(
        getattr(
            candle,
            "close",
            0.0,
        )
    )

    if open_price == 0.0:
        return 0.0

    return (
        (close_price - open_price)
        /
        abs(open_price)
    ) * 100.0


def candle_direction(
    candle,
) -> VolumeDirection:
    """
    Determine candle direction from open and close.
    """

    open_price = safe_float(
        getattr(
            candle,
            "open",
            0.0,
        )
    )

    close_price = safe_float(
        getattr(
            candle,
            "close",
            0.0,
        )
    )

    if close_price > open_price:

        return VolumeDirection.BULLISH

    if close_price < open_price:

        return VolumeDirection.BEARISH

    return VolumeDirection.NEUTRAL


# =============================================================================
# CANDLE RANGE / BODY
# =============================================================================


def candle_range(
    candle,
) -> float:
    """
    Return candle high-low range.
    """

    high = safe_float(
        getattr(
            candle,
            "high",
            0.0,
        )
    )

    low = safe_float(
        getattr(
            candle,
            "low",
            0.0,
        )
    )

    return max(
        0.0,
        high - low,
    )


def candle_body(
    candle,
) -> float:
    """
    Return absolute candle body.
    """

    return abs(
        safe_float(
            getattr(
                candle,
                "close",
                0.0,
            )
        )
        -
        safe_float(
            getattr(
                candle,
                "open",
                0.0,
            )
        )
    )


def body_ratio(
    candle,
) -> float:
    """
    Return body size relative to candle range.
    """

    total_range = candle_range(
        candle
    )

    if total_range <= 0.0:
        return 0.0

    return (
        candle_body(candle)
        /
        total_range
    )


# =============================================================================
# VOLUME SERIES
# =============================================================================


def volume_series(
    candles,
) -> list[float]:
    """
    Extract volume values from candles.
    """

    return [
        candle_volume(candle)
        for candle in candles
    ]


def rolling_average_volume(
    candles,
    period: int,
) -> list[float]:
    """
    Calculate rolling simple average volume.

    The returned list has the same length as candles.

    For the first candles, the available history is used.
    """

    if not candles:
        return []

    if period <= 0:
        period = 1

    volumes = volume_series(
        candles
    )

    averages: list[float] = []

    for index in range(
        len(volumes)
    ):

        start = max(
            0,
            index - period + 1,
        )

        window = volumes[
            start:index + 1
        ]

        if not window:

            averages.append(0.0)

        else:

            averages.append(
                sum(window)
                /
                len(window)
            )

    return averages


def relative_volume_series(
    candles,
    period: int,
) -> list[float]:
    """
    Calculate rolling Relative Volume.
    """

    if not candles:
        return []

    volumes = volume_series(
        candles
    )

    averages = rolling_average_volume(
        candles,
        period,
    )

    return [
        relative_volume(
            volume,
            average,
        )
        for volume, average
        in zip(
            volumes,
            averages,
        )
    ]


# =============================================================================
# TREND
# =============================================================================


def simple_slope(
    values: list[float],
) -> float:
    """
    Calculate a simple least-squares slope.

    X values are treated as:
        0, 1, 2, ..., n-1
    """

    if len(values) < 2:
        return 0.0

    n = len(values)

    x_mean = (
        n - 1
    ) / 2.0

    y_mean = (
        sum(values)
        /
        n
    )

    numerator = 0.0

    denominator = 0.0

    for index, value in enumerate(
        values
    ):

        x_delta = (
            index
            -
            x_mean
        )

        y_delta = (
            value
            -
            y_mean
        )

        numerator += (
            x_delta
            *
            y_delta
        )

        denominator += (
            x_delta
            *
            x_delta
        )

    if denominator <= 0.0:
        return 0.0

    return numerator / denominator


def volume_trend_direction(
    values: list[float],
) -> VolumeDirection:
    """
    Determine volume trend direction from slope.
    """

    if len(values) < 2:
        return VolumeDirection.NEUTRAL

    slope = simple_slope(
        values
    )

    if slope > 0.0:

        return VolumeDirection.BULLISH

    if slope < 0.0:

        return VolumeDirection.BEARISH

    return VolumeDirection.NEUTRAL


# =============================================================================
# SPIKE
# =============================================================================


def is_volume_spike(
    relative: float,
    threshold: float,
) -> bool:
    """
    Determine whether relative volume exceeds a threshold.
    """

    return (
        safe_float(relative)
        >=
        safe_float(threshold)
    )


def volume_spike_strength(
    relative: float,
) -> float:
    """
    Convert Relative Volume into a 0-100 spike strength.

    This is intentionally capped. A 10x reading should not create an
    unbounded score.
    """

    relative = max(
        0.0,
        safe_float(relative),
    )

    if relative <= 1.0:
        return 0.0

    strength = (
        relative - 1.0
    ) * 50.0

    return min(
        100.0,
        strength,
    )


# =============================================================================
# VOLUME TYPE
# =============================================================================


def normalize_volume_type(
    value,
) -> VolumeType:
    """
    Normalize a volume source identifier.
    """

    if value is None:

        return VolumeType.UNKNOWN

    value = str(
        value
    ).lower().strip()

    if value in (
        "tick",
        "tick_volume",
        "ticks",
    ):

        return VolumeType.TICK

    if value in (
        "real",
        "real_volume",
        "exchange",
        "trade",
    ):

        return VolumeType.REAL

    return VolumeType.UNKNOWN


# =============================================================================
# COMPARISON HELPERS
# =============================================================================


def volume_increasing(
    current: float,
    previous: float,
) -> bool:
    """
    Return True if volume increased.
    """

    return (
        safe_float(current)
        >
        safe_float(previous)
    )


def volume_decreasing(
    current: float,
    previous: float,
) -> bool:
    """
    Return True if volume decreased.
    """

    return (
        safe_float(current)
        <
        safe_float(previous)
    )


def normalize_score(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    """
    Clamp a score to a defined range.
    """

    if maximum <= minimum:
        return minimum

    value = safe_float(
        value
    )

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )
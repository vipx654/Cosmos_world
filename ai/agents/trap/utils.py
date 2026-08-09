"""
===============================================================================
COSMOS Trap Agent Utilities

Reusable price-action calculations for the Trap Agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from math import isfinite

from ai.agents.trap.constants import (
    MIN_CANDLE_RANGE,
)

from ai.agents.trap.models import (
    TrapDirection,
)


# =============================================================================
# GENERIC CANDLE ACCESS
# =============================================================================


def candle_value(
    candle,
    field: str,
    default: float = 0.0,
) -> float:
    """
    Safely retrieve a numeric candle field.

    Supports both dictionaries and objects.
    """

    try:

        if isinstance(
            candle,
            dict,
        ):

            value = candle.get(
                field,
                default,
            )

        else:

            value = getattr(
                candle,
                field,
                default,
            )

        if value is None:

            return default

        value = float(
            value
        )

        if not isfinite(
            value
        ):

            return default

        return value

    except (
        TypeError,
        ValueError,
    ):

        return default


# =============================================================================
# OHLC
# =============================================================================


def candle_open(
    candle,
) -> float:

    return candle_value(
        candle,
        "open",
    )


def candle_high(
    candle,
) -> float:

    return candle_value(
        candle,
        "high",
    )


def candle_low(
    candle,
) -> float:

    return candle_value(
        candle,
        "low",
    )


def candle_close(
    candle,
) -> float:

    return candle_value(
        candle,
        "close",
    )


def candle_volume(
    candle,
) -> float:

    return max(
        0.0,
        candle_value(
            candle,
            "volume",
        ),
    )


# =============================================================================
# RANGE / BODY
# =============================================================================


def candle_range(
    candle,
) -> float:
    """
    Total high-low range.
    """

    value = (
        candle_high(candle)
        -
        candle_low(candle)
    )

    return max(
        0.0,
        value,
    )


def candle_body(
    candle,
) -> float:
    """
    Absolute candle body size.
    """

    return abs(
        candle_close(candle)
        -
        candle_open(candle)
    )


def body_ratio(
    candle,
) -> float:
    """
    Body size as a fraction of the complete candle range.
    """

    range_value = candle_range(
        candle
    )

    if range_value <= MIN_CANDLE_RANGE:

        return 0.0

    return min(
        1.0,
        candle_body(candle)
        /
        range_value,
    )


# =============================================================================
# WICKS
# =============================================================================


def upper_wick(
    candle,
) -> float:
    """
    Distance from candle body high to candle high.
    """

    high = candle_high(
        candle
    )

    open_price = candle_open(
        candle
    )

    close_price = candle_close(
        candle
    )

    body_high = max(
        open_price,
        close_price,
    )

    return max(
        0.0,
        high - body_high,
    )


def lower_wick(
    candle,
) -> float:
    """
    Distance from candle low to candle body low.
    """

    low = candle_low(
        candle
    )

    open_price = candle_open(
        candle
    )

    close_price = candle_close(
        candle
    )

    body_low = min(
        open_price,
        close_price,
    )

    return max(
        0.0,
        body_low - low,
    )


def upper_wick_ratio(
    candle,
) -> float:
    """
    Upper wick as a fraction of total candle range.
    """

    range_value = candle_range(
        candle
    )

    if range_value <= MIN_CANDLE_RANGE:

        return 0.0

    return min(
        1.0,
        upper_wick(candle)
        /
        range_value,
    )


def lower_wick_ratio(
    candle,
) -> float:
    """
    Lower wick as a fraction of total candle range.
    """

    range_value = candle_range(
        candle
    )

    if range_value <= MIN_CANDLE_RANGE:

        return 0.0

    return min(
        1.0,
        lower_wick(candle)
        /
        range_value,
    )


# =============================================================================
# CLOSE POSITION
# =============================================================================


def close_position(
    candle,
) -> float:
    """
    Position of close inside candle range.

    Returns:

        0.0 -> close at low
        0.5 -> close at midpoint
        1.0 -> close at high
    """

    low = candle_low(
        candle
    )

    high = candle_high(
        candle
    )

    range_value = (
        high - low
    )

    if range_value <= MIN_CANDLE_RANGE:

        return 0.5

    value = (
        candle_close(candle)
        -
        low
    ) / range_value

    return max(
        0.0,
        min(
            1.0,
            value,
        ),
    )


# =============================================================================
# CANDLE DIRECTION
# =============================================================================


def candle_direction(
    candle,
) -> TrapDirection:
    """
    Determine candle direction.
    """

    open_price = candle_open(
        candle
    )

    close_price = candle_close(
        candle
    )

    if close_price > open_price:

        return TrapDirection.BULLISH

    if close_price < open_price:

        return TrapDirection.BEARISH

    return TrapDirection.NEUTRAL


# =============================================================================
# PRICE DISTANCE
# =============================================================================


def distance_from_level(
    price: float,
    level: float,
) -> float:
    """
    Absolute distance between price and level.
    """

    return abs(
        float(price)
        -
        float(level)
    )


def extension_above_level(
    high: float,
    level: float,
) -> float:
    """
    Amount price extends above a resistance level.
    """

    return max(
        0.0,
        float(high)
        -
        float(level),
    )


def extension_below_level(
    low: float,
    level: float,
) -> float:
    """
    Amount price extends below a support level.
    """

    return max(
        0.0,
        float(level)
        -
        float(low),
    )


# =============================================================================
# NORMALIZATION
# =============================================================================


def normalize_score(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    """
    Clamp a numeric score to a specified range.
    """

    if maximum <= minimum:

        return minimum

    try:

        value = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return minimum

    if not isfinite(
        value
    ):

        return minimum

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# =============================================================================
# RELATIVE VOLUME
# =============================================================================


def average_volume(
    candles,
) -> float:
    """
    Calculate average volume.
    """

    values = [
        candle_volume(
            candle
        )
        for candle in candles
    ]

    if not values:

        return 0.0

    return (
        sum(values)
        /
        len(values)
    )


def relative_volume(
    current_volume: float,
    average: float,
) -> float:
    """
    Calculate current volume relative to average volume.
    """

    if average <= 0.0:

        return 0.0

    return (
        float(current_volume)
        /
        float(average)
    )


# =============================================================================
# RANGE NORMALIZATION
# =============================================================================


def extension_ratio(
    extension: float,
    candle_range_value: float,
) -> float:
    """
    Express breakout extension as a fraction of candle range.
    """

    if candle_range_value <= MIN_CANDLE_RANGE:

        return 0.0

    return max(
        0.0,
        float(extension)
        /
        float(candle_range_value),
    )


# =============================================================================
# LEVEL RECLAIM
# =============================================================================


def reclaimed_above(
    close: float,
    level: float,
) -> bool:
    """
    Determine whether price closed back above a level.
    """

    return (
        float(close)
        >
        float(level)
    )


def reclaimed_below(
    close: float,
    level: float,
) -> bool:
    """
    Determine whether price closed back below a level.
    """

    return (
        float(close)
        <
        float(level)
    )


# =============================================================================
# TRAP-SPECIFIC CLOSE TESTS
# =============================================================================


def failed_breakout_above(
    candle,
    resistance: float,
) -> bool:
    """
    Price traded above resistance but closed back below it.

    This is a basic false-breakout condition, not a complete trap confirmation.
    """

    return (
        candle_high(candle)
        >
        resistance
        and
        candle_close(candle)
        <
        resistance
    )


def failed_breakout_below(
    candle,
    support: float,
) -> bool:
    """
    Price traded below support but closed back above it.

    This is a basic false-breakdown condition, not a complete trap confirmation.
    """

    return (
        candle_low(candle)
        <
        support
        and
        candle_close(candle)
        >
        support
    )


# =============================================================================
# RECENT AVERAGES
# =============================================================================


def average_range(
    candles,
) -> float:
    """
    Average candle range.
    """

    ranges = [
        candle_range(
            candle
        )
        for candle in candles
    ]

    if not ranges:

        return 0.0

    return (
        sum(ranges)
        /
        len(ranges)
    )


def recent_candles(
    candles,
    count: int,
):
    """
    Return the most recent `count` candles.
    """

    if candles is None:

        return []

    try:

        candle_list = list(
            candles
        )

    except TypeError:

        return []

    if count <= 0:

        return []

    return candle_list[
        -count:
    ]


# =============================================================================
# PRICE CHANGE
# =============================================================================


def price_change(
    start_price: float,
    end_price: float,
) -> float:

    return (
        float(end_price)
        -
        float(start_price)
    )


def price_change_ratio(
    start_price: float,
    end_price: float,
) -> float:
    """
    Percentage-style price change ratio.

    Example:

        100 -> 105 = 0.05
    """

    start_price = float(
        start_price
    )

    if abs(
        start_price
    ) <= MIN_CANDLE_RANGE:

        return 0.0

    return (
        float(end_price)
        -
        start_price
    ) / abs(
        start_price
    )


# =============================================================================
# RANGE HIGH / LOW
# =============================================================================


def range_high(
    candles,
) -> float:
    """
    Highest high across candles.
    """

    values = [
        candle_high(
            candle
        )
        for candle in candles
    ]

    if not values:

        return 0.0

    return max(
        values
    )


def range_low(
    candles,
) -> float:
    """
    Lowest low across candles.
    """

    values = [
        candle_low(
            candle
        )
        for candle in candles
    ]

    if not values:

        return 0.0

    return min(
        values
    )
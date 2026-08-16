"""
===============================================================================
COSMOS Trend Agent Utilities

Reusable numerical and market-analysis helpers for the Trend Agent.

These utilities intentionally contain no agent state and no chart/frontend
logic. They provide deterministic calculations used by multiple Trend engines.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from collections.abc import Sequence
from math import isfinite

from ai.agents.trend.constants import EPSILON


# =============================================================================
# NUMERICAL SAFETY
# =============================================================================


def safe_float(
    value: float | int | None,
    default: float = 0.0,
) -> float:
    """
    Convert a value to a finite float.

    Invalid, NaN and infinite values return the supplied default.
    """

    try:
        result = float(value)
    except (TypeError, ValueError):

        return default

    if not isfinite(result):

        return default

    return result


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    """
    Clamp a numeric value to a specified range.
    """

    value = safe_float(value)

    if minimum > maximum:

        minimum, maximum = maximum, minimum

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# =============================================================================
# PERCENTAGE / PRICE CHANGE
# =============================================================================


def percentage_change(
    first: float,
    second: float,
) -> float:
    """
    Percentage change from first value to second value.

    Existing COSMOS behavior is preserved:
    zero-valued reference returns 0.0.
    """

    first = safe_float(first)
    second = safe_float(second)

    if abs(first) <= EPSILON:

        return 0.0

    return (
        (second - first)
        / first
    ) * 100.0


def absolute_percentage_distance(
    first: float,
    second: float,
) -> float:
    """
    Absolute percentage distance between two values.
    """

    return abs(
        percentage_change(
            first,
            second,
        )
    )


# =============================================================================
# SERIES HELPERS
# =============================================================================


def mean(
    values: Sequence[float],
) -> float:
    """
    Arithmetic mean of a numeric sequence.
    """

    if not values:

        return 0.0

    valid = [
        safe_float(value)
        for value in values
    ]

    return sum(valid) / len(valid)


def latest(
    values: Sequence[float],
    default: float = 0.0,
) -> float:
    """
    Return the latest value from a sequence.
    """

    if not values:

        return default

    return safe_float(
        values[-1],
        default,
    )


def difference(
    first: float,
    second: float,
) -> float:
    """
    Return second - first.
    """

    return (
        safe_float(second)
        - safe_float(first)
    )


# =============================================================================
# SLOPE / VELOCITY
# =============================================================================


def slope(
    values: Sequence[float],
    lookback: int | None = None,
) -> float:
    """
    Calculate a simple average slope over a sequence.

    This is intentionally deterministic and lightweight. More advanced
    regression-based calculations can be layered on top later.
    """

    if len(values) < 2:

        return 0.0

    if lookback is not None:

        if lookback < 2:

            return 0.0

        values = values[-lookback:]

    if len(values) < 2:

        return 0.0

    first = safe_float(values[0])
    last = safe_float(values[-1])

    periods = len(values) - 1

    if periods <= 0:

        return 0.0

    return (
        last - first
    ) / periods


def normalized_slope(
    values: Sequence[float],
    lookback: int | None = None,
) -> float:
    """
    Calculate slope normalized by the first value.

    Useful when comparing momentum/trend behavior across instruments
    with different price scales.
    """

    if len(values) < 2:

        return 0.0

    if lookback is not None:

        values = values[-lookback:]

    first = safe_float(values[0])

    if abs(first) <= EPSILON:

        return 0.0

    raw_slope = slope(values)

    return (
        raw_slope / abs(first)
    )


# =============================================================================
# MOMENTUM HELPERS
# =============================================================================


def velocity(
    values: Sequence[float],
    lookback: int = 1,
) -> float:
    """
    Price velocity over a specified number of observations.
    """

    if lookback <= 0:

        return 0.0

    if len(values) <= lookback:

        return 0.0

    current = safe_float(
        values[-1]
    )

    previous = safe_float(
        values[-1 - lookback]
    )

    return current - previous


def percentage_velocity(
    values: Sequence[float],
    lookback: int = 1,
) -> float:
    """
    Percentage price velocity.
    """

    if lookback <= 0:

        return 0.0

    if len(values) <= lookback:

        return 0.0

    return percentage_change(
        values[-1 - lookback],
        values[-1],
    )


def acceleration(
    values: Sequence[float],
    lookback: int = 1,
) -> float:
    """
    Second-order price movement.

    Positive values indicate increasing velocity;
    negative values indicate decreasing velocity.
    """

    if lookback <= 0:

        return 0.0

    if len(values) <= lookback * 2:

        return 0.0

    current_velocity = velocity(
        values,
        lookback,
    )

    previous_values = values[:-lookback]

    previous_velocity = velocity(
        previous_values,
        lookback,
    )

    return (
        current_velocity
        - previous_velocity
    )


# =============================================================================
# RANGE HELPERS
# =============================================================================


def true_range(
    high: float,
    low: float,
    previous_close: float | None = None,
) -> float:
    """
    Calculate True Range for a single candle.
    """

    high = safe_float(high)
    low = safe_float(low)

    if previous_close is None:

        return max(
            0.0,
            high - low,
        )

    previous_close = safe_float(
        previous_close
    )

    return max(
        high - low,
        abs(high - previous_close),
        abs(low - previous_close),
    )


def average_true_range(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    period: int = 14,
) -> float:
    """
    Lightweight ATR calculation.

    Uses simple averaging to remain deterministic and dependency-free.
    """

    if period <= 0:

        return 0.0

    if not highs or not lows or not closes:

        return 0.0

    size = min(
        len(highs),
        len(lows),
        len(closes),
    )

    if size < 2:

        return 0.0

    start = max(
        1,
        size - period,
    )

    ranges: list[float] = []

    for index in range(
        start,
        size,
    ):

        ranges.append(
            true_range(
                highs[index],
                lows[index],
                closes[index - 1],
            )
        )

    if not ranges:

        return 0.0

    return mean(ranges)


# =============================================================================
# DIRECTION HELPERS
# =============================================================================


def direction(
    first: float,
    second: float,
    tolerance: float = 0.0,
) -> int:
    """
    Compare two values.

    Returns:
        1  -> upward
        0  -> effectively unchanged
        -1 -> downward
    """

    first = safe_float(first)
    second = safe_float(second)
    tolerance = abs(
        safe_float(tolerance)
    )

    delta = second - first

    if delta > tolerance:

        return 1

    if delta < -tolerance:

        return -1

    return 0


def is_rising(
    values: Sequence[float],
    tolerance: float = 0.0,
) -> bool:
    """
    Determine whether the latest value is above the previous value.
    """

    if len(values) < 2:

        return False

    return (
        direction(
            values[-2],
            values[-1],
            tolerance,
        )
        > 0
    )


def is_falling(
    values: Sequence[float],
    tolerance: float = 0.0,
) -> bool:
    """
    Determine whether the latest value is below the previous value.
    """

    if len(values) < 2:

        return False

    return (
        direction(
            values[-2],
            values[-1],
            tolerance,
        )
        < 0
    )


# =============================================================================
# QUALITY HELPERS
# =============================================================================


def has_minimum_values(
    values: Sequence[object],
    minimum: int,
) -> bool:
    """
    Check whether a sequence contains the required number of observations.
    """

    return len(values) >= max(
        0,
        minimum,
    )


def finite_series(
    values: Sequence[float],
) -> bool:
    """
    Verify that every value in a series is finite.
    """

    return all(
        isfinite(
            safe_float(value)
        )
        for value in values
    )
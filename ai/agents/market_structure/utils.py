"""
===============================================================================
COSMOS Market Structure Utils

Reusable helper functions for Market Structure Agent.

Responsibilities:

    - Structure calculations
    - Safe comparisons
    - Confidence normalization
    - Numeric validation

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations


# =============================================================================
# PRICE UTILITIES
# =============================================================================


def price_distance(
    first: float,
    second: float,
) -> float:
    """
    Calculates absolute price distance.
    """

    return abs(

        float(first)

        -

        float(second)

    )


# =============================================================================
# STRUCTURE COMPARISON
# =============================================================================


def is_higher(
    current: float,
    previous: float,
) -> bool:
    """
    Checks if current price forms a higher structure.
    """

    return (

        float(current)

        >

        float(previous)

    )


def is_lower(
    current: float,
    previous: float,
) -> bool:
    """
    Checks if current price forms a lower structure.
    """

    return (

        float(current)

        <

        float(previous)

    )


# =============================================================================
# CONFIDENCE HELPERS
# =============================================================================


def clamp_confidence(
    value: float,
) -> float:
    """
    Keeps confidence between 0 and 100.
    """

    return round(

        max(

            0.0,

            min(

                100.0,

                float(value),

            ),

        ),

        2,

    )


# =============================================================================
# STRENGTH HELPERS
# =============================================================================


def calculate_strength(
    positive: int,
    negative: int,
) -> float:
    """
    Calculates structural dominance percentage.

    Example:

        positive = 3
        negative = 1

        result = 75%
    """

    positive = max(

        0,

        int(positive),

    )

    negative = max(

        0,

        int(negative),

    )

    total = positive + negative

    if total == 0:

        return 0.0

    return round(

        (

            positive

            /

            total

        )

        *

        100.0,

        2,

    )


# =============================================================================
# INDEX UTILITIES
# =============================================================================


def index_distance(
    first: int,
    second: int,
) -> int:
    """
    Calculates distance between swing indexes.
    """

    return abs(

        int(first)

        -

        int(second)

    )
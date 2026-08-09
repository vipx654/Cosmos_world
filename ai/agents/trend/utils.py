"""
===============================================================================
COSMOS Trend Utilities
===============================================================================
"""


def percentage_change(
    first: float,
    second: float,
) -> float:
    """
    Percentage difference.
    """

    if first == 0:
        return 0.0

    return ((second - first) / first) * 100
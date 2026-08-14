"""
===============================================================================
COSMOS Sweep Utilities

Production utility functions for Sweep Agent analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from collections.abc import Iterable

from ai.agents.sweep.models import (
    SweepObject,
    SweepStatus,
)


def _valid_sweeps(
    sweeps: Iterable[SweepObject] | None,
) -> list[SweepObject]:
    """
    Return only valid SweepObject instances.

    The original objects are preserved; no copies are created.
    """

    if sweeps is None:
        return []

    return [
        sweep
        for sweep in sweeps
        if isinstance(
            sweep,
            SweepObject,
        )
    ]


def _score(
    value: float,
) -> float:
    """
    Normalize a Sweep score to the valid 0-100 range.
    """

    try:
        numeric_value = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    if numeric_value != numeric_value:
        return 0.0

    if numeric_value == float("inf"):
        return 100.0

    if numeric_value == float("-inf"):
        return 0.0

    return max(
        0.0,
        min(
            100.0,
            numeric_value,
        ),
    )


def strongest_sweep(
    sweeps: Iterable[SweepObject] | None,
) -> SweepObject | None:
    """
    Return the sweep with the highest strength.

    Returns None when no valid sweeps are available.
    """

    valid = _valid_sweeps(
        sweeps
    )

    if not valid:
        return None

    return max(
        valid,
        key=lambda sweep: _score(
            sweep.strength
        ),
    )


def weakest_sweep(
    sweeps: Iterable[SweepObject] | None,
) -> SweepObject | None:
    """
    Return the sweep with the lowest strength.

    Returns None when no valid sweeps are available.
    """

    valid = _valid_sweeps(
        sweeps
    )

    if not valid:
        return None

    return min(
        valid,
        key=lambda sweep: _score(
            sweep.strength
        ),
    )


def average_probability(
    sweeps: Iterable[SweepObject] | None,
) -> float:
    """
    Calculate the average probability of valid sweeps.
    """

    valid = _valid_sweeps(
        sweeps
    )

    if not valid:
        return 0.0

    total = sum(
        _score(
            sweep.probability
        )
        for sweep in valid
    )

    return round(
        total / len(valid),
        2,
    )


def average_confidence(
    sweeps: Iterable[SweepObject] | None,
) -> float:
    """
    Calculate the average confidence of valid sweeps.
    """

    valid = _valid_sweeps(
        sweeps
    )

    if not valid:
        return 0.0

    total = sum(
        _score(
            sweep.confidence
        )
        for sweep in valid
    )

    return round(
        total / len(valid),
        2,
    )


def confirmed_sweeps(
    sweeps: Iterable[SweepObject] | None,
) -> list[SweepObject]:
    """
    Return sweeps whose lifecycle status is CONFIRMED.
    """

    valid = _valid_sweeps(
        sweeps
    )

    return [
        sweep
        for sweep in valid
        if sweep.status
        is SweepStatus.CONFIRMED
    ]


def fake_sweeps(
    sweeps: Iterable[SweepObject] | None,
) -> list[SweepObject]:
    """
    Return sweeps explicitly marked as fake.
    """

    valid = _valid_sweeps(
        sweeps
    )

    return [
        sweep
        for sweep in valid
        if sweep.fake is True
    ]
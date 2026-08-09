"""
===============================================================================
COSMOS Sweep Utilities

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.sweep.models import (
    SweepObject,
)


def strongest_sweep(
    sweeps: list[SweepObject],
) -> SweepObject | None:
    """
    Returns the strongest sweep.
    """

    if not sweeps:
        return None

    return max(
        sweeps,
        key=lambda x: x.strength,
    )


def weakest_sweep(
    sweeps: list[SweepObject],
) -> SweepObject | None:
    """
    Returns the weakest sweep.
    """

    if not sweeps:
        return None

    return min(
        sweeps,
        key=lambda x: x.strength,
    )


def average_probability(
    sweeps: list[SweepObject],
) -> float:
    """
    Average probability.
    """

    if not sweeps:
        return 0.0

    return round(
        sum(
            x.probability
            for x in sweeps
        )
        / len(sweeps),
        2,
    )


def average_confidence(
    sweeps: list[SweepObject],
) -> float:
    """
    Average confidence.
    """

    if not sweeps:
        return 0.0

    return round(
        sum(
            x.confidence
            for x in sweeps
        )
        / len(sweeps),
        2,
    )


def confirmed_sweeps(
    sweeps: list[SweepObject],
) -> list[SweepObject]:
    """
    Returns confirmed sweeps.
    """

    return [
        sweep
        for sweep in sweeps
        if sweep.status.value == "CONFIRMED"
    ]


def fake_sweeps(
    sweeps: list[SweepObject],
) -> list[SweepObject]:
    """
    Returns fake sweeps.
    """

    return [
        sweep
        for sweep in sweeps
        if sweep.fake
    ]
"""
===============================================================================
COSMOS Sweep Probability Engine

Calculates probability of a detected liquidity sweep.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.sweep.models import SweepObject


class ProbabilityEngine:
    """
    Calculates probability for detected sweeps.

    V1 Factors
    ----------
    - Confidence
    - Strength

    V2 Factors
    ----------
    - Trend
    - BOS
    - CHOCH
    - Volume
    - Session
    - FVG
    - Order Block
    """

    def calculate(
        self,
        sweeps: list[SweepObject],
    ) -> list[SweepObject]:

        for sweep in sweeps:

            probability = (
                sweep.confidence * 0.60
                +
                sweep.strength * 0.40
            )

            probability = max(
                0.0,
                min(
                    100.0,
                    probability,
                ),
            )

            sweep.probability = round(
                probability,
                2,
            )

            sweep.evidence.append(
                "Probability Calculated"
            )

        return sweeps
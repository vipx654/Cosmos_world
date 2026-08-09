"""
===============================================================================
COSMOS Sweep Confidence Engine

Calculates confidence for detected liquidity sweeps.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.sweep.models import SweepObject


class ConfidenceEngine:
    """
    Calculates institutional confidence.

    V1 Factors
    ----------
    - Sweep Strength
    - Probability

    V2 Factors
    ----------
    - Trend
    - Volume
    - Session
    - BOS
    - CHOCH
    - FVG
    - Order Block
    """

    def calculate(
        self,
        sweeps: list[SweepObject],
    ) -> float:

        if not sweeps:
            return 0.0

        total = 0.0

        for sweep in sweeps:

            confidence = (

                sweep.strength * 0.50

                +

                sweep.probability * 0.50

            )

            confidence = max(
                0.0,
                min(
                    100.0,
                    confidence,
                ),
            )

            sweep.confidence = round(
                confidence,
                2,
            )

            sweep.evidence.append(
                "Confidence Calculated"
            )

            total += confidence

        return round(
            total / len(sweeps),
            2,
        )
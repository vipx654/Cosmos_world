"""
===============================================================================
COSMOS Liquidity Quality Engine

Evaluates institutional quality of liquidity.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.liquidity.models import (
    LiquidityObject,
)


class QualityEngine:
    """
    Calculates institutional quality score
    for every liquidity object.
    """

    def analyze(
        self,
        liquidity: list[LiquidityObject],
    ) -> list[LiquidityObject]:

        for level in liquidity:

            score = 0.0

            # ---------------------------------------------------------
            # Touches
            # ---------------------------------------------------------

            score += min(
                level.touches * 12,
                40,
            )

            # ---------------------------------------------------------
            # Strength
            # ---------------------------------------------------------

            score += min(
                level.strength * 0.30,
                30,
            )

            # ---------------------------------------------------------
            # Confidence
            # ---------------------------------------------------------

            score += min(
                level.confidence * 0.30,
                30,
            )

            level.quality = round(
                min(score, 100),
                2,
            )

        return liquidity
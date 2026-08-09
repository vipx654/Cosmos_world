"""
===============================================================================
COSMOS Order Block Probability Engine

Calculates probability for detected order blocks.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.order_block.models import OrderBlock


class ProbabilityEngine:
    """
    Calculates V1 order-block probability.

    V1 weighting:

    Confidence -> 40%
    Strength   -> 35%
    Validity   -> 25%

    Future versions can incorporate:

    - Trend alignment
    - Liquidity
    - Sweep confirmation
    - FVG
    - Volume
    - Session
    - Historical performance
    """

    def calculate(
        self,
        blocks: list[OrderBlock],
    ) -> list[OrderBlock]:

        for block in blocks:

            confidence = max(
                0.0,
                min(
                    100.0,
                    float(block.confidence),
                ),
            )

            strength = max(
                0.0,
                min(
                    100.0,
                    float(block.strength),
                ),
            )

            validity_score = (
                100.0
                if block.valid
                else 0.0
            )

            probability = (
                confidence * 0.40
                +
                strength * 0.35
                +
                validity_score * 0.25
            )

            probability = max(
                0.0,
                min(
                    100.0,
                    probability,
                ),
            )

            block.probability = round(
                probability,
                2,
            )

            block.evidence.append(
                "Probability Calculated"
            )

        return blocks
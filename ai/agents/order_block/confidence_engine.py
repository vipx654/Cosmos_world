"""
===============================================================================
COSMOS Order Block Confidence Engine

Calculates the final confidence of detected order blocks.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.order_block.models import OrderBlock


class ConfidenceEngine:
    """
    Calculates overall Order Block confidence.

    V1 weighting:

    Probability -> 50%
    Strength    -> 30%
    Validity    -> 20%

    This is intentionally simple for V1.
    Advanced structural confirmation will be added later.
    """

    def calculate(
        self,
        blocks: list[OrderBlock],
    ) -> float:

        if not blocks:
            return 0.0

        total_confidence = 0.0

        for block in blocks:

            probability = max(
                0.0,
                min(
                    100.0,
                    float(block.probability),
                ),
            )

            strength = max(
                0.0,
                min(
                    100.0,
                    float(block.strength),
                ),
            )

            validity = (
                100.0
                if block.valid
                else 0.0
            )

            confidence = (
                probability * 0.50
                +
                strength * 0.30
                +
                validity * 0.20
            )

            confidence = max(
                0.0,
                min(
                    100.0,
                    confidence,
                ),
            )

            block.confidence = round(
                confidence,
                2,
            )

            block.evidence.append(
                "Confidence Calculated"
            )

            total_confidence += confidence

        return round(
            total_confidence / len(blocks),
            2,
        )
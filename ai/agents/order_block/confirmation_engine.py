"""
===============================================================================
COSMOS Order Block Confirmation Engine

Confirms detected order blocks using structural and quality factors.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.order_block.constants import (
    HIGH_CONFIDENCE,
    HIGH_PROBABILITY,
    HIGH_STRENGTH,
    MIN_CONFIRMATION_SCORE,
)

from ai.agents.order_block.models import (
    OrderBlock,
    OrderBlockConfirmation,
)


class ConfirmationEngine:
    """
    Confirms order blocks.

    V1 confirmation factors:

    - Confidence
    - Probability
    - Strength
    - Validity

    Future versions can add:

    - BOS
    - CHOCH
    - Liquidity sweep
    - FVG
    - Trend alignment
    - Volume
    - Session
    """

    def analyze(
        self,
        blocks: list[OrderBlock],
    ) -> list[OrderBlockConfirmation]:

        results: list[OrderBlockConfirmation] = []

        for block in blocks:

            score = 0

            reasons: list[str] = []

            # -----------------------------------------------------------------
            # Valid block
            # -----------------------------------------------------------------

            if block.valid:

                score += 1

                reasons.append(
                    "Block Valid"
                )

            # -----------------------------------------------------------------
            # Confidence
            # -----------------------------------------------------------------

            if block.confidence >= HIGH_CONFIDENCE:

                score += 1

                reasons.append(
                    "High Confidence"
                )

            # -----------------------------------------------------------------
            # Probability
            # -----------------------------------------------------------------

            if block.probability >= HIGH_PROBABILITY:

                score += 1

                reasons.append(
                    "High Probability"
                )

            # -----------------------------------------------------------------
            # Strength
            # -----------------------------------------------------------------

            if block.strength >= HIGH_STRENGTH:

                score += 1

                reasons.append(
                    "High Strength"
                )

            # -----------------------------------------------------------------
            # Calculate normalized confirmation score.
            # -----------------------------------------------------------------

            max_score = 4

            normalized_score = (
                score / max_score
            ) * 100.0

            confirmed = (
                score >= MIN_CONFIRMATION_SCORE
                and block.valid
            )

            if confirmed:

                block.evidence.append(
                    "Order Block Confirmed"
                )

            else:

                block.evidence.append(
                    "Order Block Not Confirmed"
                )

            results.append(
                OrderBlockConfirmation(

                    order_block=block,

                    confirmed=confirmed,

                    score=round(
                        normalized_score,
                        2,
                    ),

                    reasons=reasons,

                )
            )

        return results
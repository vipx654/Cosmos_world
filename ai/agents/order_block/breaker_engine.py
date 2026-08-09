"""
===============================================================================
COSMOS Order Block Breaker Engine

Detects Order Blocks that have failed and become breaker blocks.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.order_block.models import (
    OrderBlock,
    OrderBlockDirection,
    OrderBlockStatus,
    OrderBlockType,
)


class BreakerEngine:
    """
    Converts invalidated order blocks into breaker blocks.

    V1 logic:

    Bullish OB invalidated
        ->
    Bearish breaker

    Bearish OB invalidated
        ->
    Bullish breaker
    """

    def analyze(
        self,
        blocks: list[OrderBlock],
    ) -> list[OrderBlock]:

        breakers: list[OrderBlock] = []

        for block in blocks:

            if block.valid:
                continue

            if block.breaker:
                continue

            original_direction = (
                block.direction
            )

            # ---------------------------------------------------------------
            # Failed bullish order block becomes bearish breaker.
            # ---------------------------------------------------------------

            if (
                block.block_type
                == OrderBlockType.BULLISH
            ):

                block.block_type = (
                    OrderBlockType.BREAKER
                )

                block.direction = (
                    OrderBlockDirection.BEARISH
                )

                block.status = (
                    OrderBlockStatus.TESTED
                )

                block.breaker = True

                block.confidence = min(
                    100.0,
                    block.confidence + 5.0,
                )

                block.probability = min(
                    100.0,
                    block.probability + 5.0,
                )

                block.strength = min(
                    100.0,
                    block.strength + 5.0,
                )

                block.evidence.append(
                    "Bullish Order Block Failed"
                )

                block.evidence.append(
                    "Converted To Bearish Breaker"
                )

                breakers.append(
                    block
                )

            # ---------------------------------------------------------------
            # Failed bearish order block becomes bullish breaker.
            # ---------------------------------------------------------------

            elif (
                block.block_type
                == OrderBlockType.BEARISH
            ):

                block.block_type = (
                    OrderBlockType.BREAKER
                )

                block.direction = (
                    OrderBlockDirection.BULLISH
                )

                block.status = (
                    OrderBlockStatus.TESTED
                )

                block.breaker = True

                block.confidence = min(
                    100.0,
                    block.confidence + 5.0,
                )

                block.probability = min(
                    100.0,
                    block.probability + 5.0,
                )

                block.strength = min(
                    100.0,
                    block.strength + 5.0,
                )

                block.evidence.append(
                    "Bearish Order Block Failed"
                )

                block.evidence.append(
                    "Converted To Bullish Breaker"
                )

                breakers.append(
                    block
                )

        return breakers
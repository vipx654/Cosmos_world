"""
===============================================================================
COSMOS Bearish Order Block Engine

Detects bearish institutional order blocks.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.order_block.constants import (
    DEFAULT_CONFIDENCE,
    DEFAULT_PROBABILITY,
    DEFAULT_STRENGTH,
    EXPANSION_MULTIPLIER,
    MIN_BODY_RATIO,
)

from ai.agents.order_block.models import (
    OrderBlock,
    OrderBlockDirection,
    OrderBlockStatus,
    OrderBlockType,
)

from ai.agents.order_block.utils import (
    body_ratio,
    candle_range,
    is_bullish_candle,
)


class BearishOrderBlockEngine:
    """
    Detects basic bearish order blocks.

    V1 concept:

    Bullish candle
        +
    Following bearish expansion
        =
    Potential bearish order block
    """

    def analyze(
        self,
        candles,
    ) -> list[OrderBlock]:

        blocks: list[OrderBlock] = []

        if len(candles) < 3:
            return blocks

        for index in range(
            1,
            len(candles) - 1,
        ):

            candle = candles[index]

            next_candle = candles[
                index + 1
            ]

            # ---------------------------------------------------------------
            # Bearish OB starts with a bullish candle.
            # ---------------------------------------------------------------

            if not is_bullish_candle(
                candle
            ):
                continue

            # ---------------------------------------------------------------
            # Ignore extremely weak candles.
            # ---------------------------------------------------------------

            if body_ratio(candle) < (
                MIN_BODY_RATIO
            ):
                continue

            current_range = candle_range(
                candle
            )

            next_range = candle_range(
                next_candle
            )

            if current_range <= 0:
                continue

            # ---------------------------------------------------------------
            # Following candle should show bearish expansion.
            # ---------------------------------------------------------------

            if next_range < (
                current_range
                *
                EXPANSION_MULTIPLIER
            ):
                continue

            if float(next_candle.close) >= float(
                candle.low
            ):
                continue

            confidence = DEFAULT_CONFIDENCE

            probability = DEFAULT_PROBABILITY

            strength = DEFAULT_STRENGTH

            evidence: list[str] = []

            evidence.append(
                "Bullish Base Candle"
            )

            evidence.append(
                "Bearish Expansion"
            )

            confidence += 10.0

            probability += 10.0

            strength += 10.0

            # ---------------------------------------------------------------
            # Strong close beyond the order-block low.
            # ---------------------------------------------------------------

            if float(next_candle.close) < (
                float(candle.low)
            ):

                confidence += 10.0

                probability += 10.0

                strength += 10.0

                evidence.append(
                    "Bearish Break From Block"
                )

            confidence = min(
                100.0,
                confidence,
            )

            probability = min(
                100.0,
                probability,
            )

            strength = min(
                100.0,
                strength,
            )

            block = OrderBlock(

                block_type=(
                    OrderBlockType.BEARISH
                ),

                status=(
                    OrderBlockStatus.FRESH
                ),

                direction=(
                    OrderBlockDirection.BEARISH
                ),

                high=float(
                    candle.high
                ),

                low=float(
                    candle.low
                ),

                candle_index=index,

                confidence=confidence,

                probability=probability,

                strength=strength,

                source=(
                    "BearishOrderBlockEngine"
                ),

                evidence=evidence,

            )

            blocks.append(
                block
            )

        return blocks
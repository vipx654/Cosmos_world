"""
===============================================================================
COSMOS Bullish Order Block Engine

Detects bullish institutional order blocks.

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
    is_bearish_candle,
)


class BullishOrderBlockEngine:
    """
    Detects basic bullish order blocks.

    V1 concept:

    Bearish candle
        +
    Following bullish expansion
        =
    Potential bullish order block
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
            # Bullish OB starts with a bearish candle.
            # ---------------------------------------------------------------

            if not is_bearish_candle(
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
            # Following candle should show bullish expansion.
            # ---------------------------------------------------------------

            if next_range < (
                current_range
                *
                EXPANSION_MULTIPLIER
            ):
                continue

            if float(next_candle.close) <= float(
                candle.high
            ):
                continue

            confidence = DEFAULT_CONFIDENCE

            probability = DEFAULT_PROBABILITY

            strength = DEFAULT_STRENGTH

            evidence: list[str] = []

            evidence.append(
                "Bearish Base Candle"
            )

            evidence.append(
                "Bullish Expansion"
            )

            confidence += 10.0

            probability += 10.0

            strength += 10.0

            # ---------------------------------------------------------------
            # Strong close beyond the order-block high.
            # ---------------------------------------------------------------

            if float(next_candle.close) > (
                float(candle.high)
            ):

                confidence += 10.0

                probability += 10.0

                strength += 10.0

                evidence.append(
                    "Bullish Break From Block"
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
                    OrderBlockType.BULLISH
                ),

                status=(
                    OrderBlockStatus.FRESH
                ),

                direction=(
                    OrderBlockDirection.BULLISH
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
                    "BullishOrderBlockEngine"
                ),

                evidence=evidence,

            )

            blocks.append(
                block
            )

        return blocks
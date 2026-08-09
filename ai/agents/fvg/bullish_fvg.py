"""
===============================================================================
COSMOS Bullish Fair Value Gap Engine

Detects bullish Fair Value Gaps using a three-candle imbalance structure.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.constants import (
    DEFAULT_CONFIDENCE,
    DEFAULT_PROBABILITY,
    DEFAULT_SOURCE,
    DEFAULT_STRENGTH,
    MIN_BODY_RATIO,
    SIGNIFICANT_GAP_RATIO,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGDirection,
    FVGStatus,
    FVGType,
)

from ai.agents.fvg.utils import (
    body_ratio,
    calculate_midpoint,
    candle_range,
    is_bullish_candle,
)


class BullishFVGEngine:
    """
    Detects bullish Fair Value Gaps.

    V1 structure:

        Candle 1 high < Candle 3 low

    This leaves an untraded price region between the first candle high
    and third candle low.

    The middle candle should demonstrate directional expansion.
    """

    def analyze(
        self,
        candles,
    ) -> list[FairValueGap]:

        fvgs: list[FairValueGap] = []

        if len(candles) < 3:
            return fvgs

        for index in range(
            0,
            len(candles) - 2,
        ):

            first = candles[index]

            middle = candles[
                index + 1
            ]

            third = candles[
                index + 2
            ]

            # -----------------------------------------------------------------
            # Bullish FVG condition.
            #
            # First candle high must be below third candle low.
            # -----------------------------------------------------------------

            first_high = float(
                first.high
            )

            third_low = float(
                third.low
            )

            if first_high >= third_low:
                continue

            gap_low = first_high

            gap_high = third_low

            gap_size = (
                gap_high
                -
                gap_low
            )

            if gap_size <= 0:
                continue

            # -----------------------------------------------------------------
            # Middle candle should show bullish intent.
            # -----------------------------------------------------------------

            middle_range = candle_range(
                middle
            )

            if middle_range <= 0:
                continue

            middle_body_ratio = body_ratio(
                middle
            )

            if (
                not is_bullish_candle(
                    middle
                )
                and
                middle_body_ratio
                < MIN_BODY_RATIO
            ):
                continue

            # -----------------------------------------------------------------
            # Estimate gap significance relative to middle candle range.
            # -----------------------------------------------------------------

            gap_ratio = (
                gap_size
                /
                middle_range
            )

            confidence = (
                DEFAULT_CONFIDENCE
            )

            probability = (
                DEFAULT_PROBABILITY
            )

            strength = (
                DEFAULT_STRENGTH
            )

            evidence: list[str] = []

            evidence.append(
                "Three Candle Imbalance"
            )

            evidence.append(
                "Bullish FVG"
            )

            # -----------------------------------------------------------------
            # Strong middle candle.
            # -----------------------------------------------------------------

            if (
                is_bullish_candle(
                    middle
                )
                and
                middle_body_ratio
                >= MIN_BODY_RATIO
            ):

                confidence += 10.0

                probability += 10.0

                strength += 10.0

                evidence.append(
                    "Bullish Middle Candle"
                )

            # -----------------------------------------------------------------
            # Significant gap.
            # -----------------------------------------------------------------

            if gap_ratio >= (
                SIGNIFICANT_GAP_RATIO
            ):

                confidence += 10.0

                probability += 10.0

                strength += 10.0

                evidence.append(
                    "Significant Gap"
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

            midpoint = calculate_midpoint(
                gap_low,
                gap_high,
            )

            fvg = FairValueGap(

                fvg_type=(
                    FVGType.BULLISH
                ),

                status=(
                    FVGStatus.FRESH
                ),

                direction=(
                    FVGDirection.BULLISH
                ),

                high=gap_high,

                low=gap_low,

                first_candle_index=index,

                middle_candle_index=(
                    index + 1
                ),

                third_candle_index=(
                    index + 2
                ),

                confidence=confidence,

                probability=probability,

                strength=strength,

                midpoint=midpoint,

                source=DEFAULT_SOURCE,

                evidence=evidence,

            )

            fvgs.append(
                fvg
            )

        return fvgs
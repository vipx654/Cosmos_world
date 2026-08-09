"""
===============================================================================
COSMOS Fair Value Gap Engine

Institutional Fair Value Gap Detection.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.context import Candle

from ai.agents.smc.constants import MIN_FVG_SIZE
from ai.agents.smc.models import (
    FairValueGap,
    FVGStatus,
    FVGType,
)


class FVGEngine:
    """
    Detects Fair Value Gaps.

    Uses a three-candle imbalance model.
    """

    def analyze(
        self,
        candles: list[Candle],
    ) -> FairValueGap:

        if len(candles) < 3:

            return FairValueGap(

                gap_type=FVGType.NONE,

                status=FVGStatus.INVALID,

                upper=0.0,

                lower=0.0,
            )

        c1 = candles[-3]

        c2 = candles[-2]

        c3 = candles[-1]

        # ---------------------------------------------------------
        # Bullish FVG
        # ---------------------------------------------------------

        if c1.high < c3.low:

            gap = c3.low - c1.high

            if gap >= MIN_FVG_SIZE:

                return FairValueGap(

                    gap_type=FVGType.BULLISH,

                    status=FVGStatus.ACTIVE,

                    upper=c3.low,

                    lower=c1.high,
                )

        # ---------------------------------------------------------
        # Bearish FVG
        # ---------------------------------------------------------

        if c1.low > c3.high:

            gap = c1.low - c3.high

            if gap >= MIN_FVG_SIZE:

                return FairValueGap(

                    gap_type=FVGType.BEARISH,

                    status=FVGStatus.ACTIVE,

                    upper=c1.low,

                    lower=c3.high,
                )

        return FairValueGap(

            gap_type=FVGType.NONE,

            status=FVGStatus.INVALID,

            upper=0.0,

            lower=0.0,
        )
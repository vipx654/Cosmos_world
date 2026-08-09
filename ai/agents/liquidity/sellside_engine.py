"""
===============================================================================
COSMOS Sell Side Liquidity Engine

Detects Sell Side Liquidity.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.liquidity.constants import (
    LIQUIDITY_TOLERANCE,
    MIN_TOUCHES,
)

from ai.agents.liquidity.models import (
    LiquidityObject,
    LiquidityStatus,
    LiquidityType,
)


class SellSideEngine:
    """
    Detects Sell Side Liquidity.

    Sell Side Liquidity forms below Equal Lows.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> list[LiquidityObject]:

        lows = [

            s

            for s in swings

            if s.swing_type == SwingType.LOW

        ]

        liquidity: list[LiquidityObject] = []

        if len(lows) < MIN_TOUCHES:

            return liquidity

        for i in range(len(lows)):

            touches = 1

            for j in range(i + 1, len(lows)):

                distance = abs(

                    lows[i].price

                    -

                    lows[j].price

                )

                if distance <= LIQUIDITY_TOLERANCE:

                    touches += 1

            if touches >= MIN_TOUCHES:

                liquidity.append(

                    LiquidityObject(

                        liquidity_type=LiquidityType.SELL_SIDE,

                        status=LiquidityStatus.UNTOUCHED,

                        price=lows[i].price,

                        touches=touches,

                        strength=min(
                            touches * 20,
                            100,
                        ),

                        confidence=min(
                            60 + touches * 10,
                            100,
                        ),
                    )
                )

        return liquidity
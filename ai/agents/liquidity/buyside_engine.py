"""
===============================================================================
COSMOS Buy Side Liquidity Engine

Detects Buy Side Liquidity.

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
    LiquidityType,
    LiquidityStatus,
)


class BuySideEngine:
    """
    Detects Buy Side Liquidity.

    Buy Side Liquidity forms above Equal Highs.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> list[LiquidityObject]:

        highs = [

            s

            for s in swings

            if s.swing_type == SwingType.HIGH

        ]

        liquidity: list[LiquidityObject] = []

        if len(highs) < MIN_TOUCHES:

            return liquidity

        for i in range(len(highs)):

            touches = 1

            for j in range(i + 1, len(highs)):

                distance = abs(

                    highs[i].price

                    -

                    highs[j].price

                )

                if distance <= LIQUIDITY_TOLERANCE:

                    touches += 1

            if touches >= MIN_TOUCHES:

                liquidity.append(

                    LiquidityObject(

                        liquidity_type=LiquidityType.BUY_SIDE,

                        status=LiquidityStatus.UNTOUCHED,

                        price=highs[i].price,

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
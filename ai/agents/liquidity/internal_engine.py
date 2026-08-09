"""
===============================================================================
COSMOS Internal Liquidity Engine

Detects Internal Liquidity.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.models import SwingPoint

from ai.agents.liquidity.models import (
    LiquidityObject,
    LiquidityType,
    LiquidityStatus,
)


class InternalLiquidityEngine:
    """
    Detects Internal Liquidity.

    Internal Liquidity exists between the
    most recent major swing high and swing low.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> list[LiquidityObject]:

        liquidity: list[LiquidityObject] = []

        if len(swings) < 4:
            return liquidity

        # Ignore first and last swing.
        # Everything inside is considered internal.

        internal_swings = swings[1:-1]

        for swing in internal_swings:

            liquidity.append(

                LiquidityObject(

                    liquidity_type=LiquidityType.INTERNAL,

                    status=LiquidityStatus.UNTOUCHED,

                    price=swing.price,

                    touches=1,

                    strength=50,

                    confidence=55,
                )
            )

        return liquidity
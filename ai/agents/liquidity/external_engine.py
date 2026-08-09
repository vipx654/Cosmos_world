"""
===============================================================================
COSMOS External Liquidity Engine

Detects External Liquidity.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.models import SwingPoint

from ai.agents.liquidity.models import (
    LiquidityObject,
    LiquidityStatus,
    LiquidityType,
)


class ExternalLiquidityEngine:
    """
    Detects External Liquidity.

    External Liquidity is usually located
    at the latest major swing high
    and latest major swing low.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> list[LiquidityObject]:

        liquidity: list[LiquidityObject] = []

        if len(swings) < 2:
            return liquidity

        highest = max(
            swings,
            key=lambda s: s.price,
        )

        lowest = min(
            swings,
            key=lambda s: s.price,
        )

        liquidity.append(

            LiquidityObject(

                liquidity_type=LiquidityType.EXTERNAL,

                status=LiquidityStatus.UNTOUCHED,

                price=highest.price,

                touches=1,

                strength=90,

                confidence=90,
            )
        )

        liquidity.append(

            LiquidityObject(

                liquidity_type=LiquidityType.EXTERNAL,

                status=LiquidityStatus.UNTOUCHED,

                price=lowest.price,

                touches=1,

                strength=90,

                confidence=90,
            )
        )

        return liquidity
"""
===============================================================================
COSMOS Liquidity Utilities

Author: COSMOS Development Team
===============================================================================
"""

from __future__ import annotations

from ai.agents.liquidity.models import (
    LiquidityObject,
)


def average_quality(
    liquidity: list[LiquidityObject],
) -> float:

    if not liquidity:

        return 0.0

    return round(

        sum(

            x.quality

            for x in liquidity

        )

        /

        len(liquidity),

        2,
    )


def strongest_liquidity(
    liquidity: list[LiquidityObject],
) -> LiquidityObject | None:

    if not liquidity:

        return None

    return max(

        liquidity,

        key=lambda x: x.quality,
    )


def weakest_liquidity(
    liquidity: list[LiquidityObject],
) -> LiquidityObject | None:

    if not liquidity:

        return None

    return min(

        liquidity,

        key=lambda x: x.quality,
    )
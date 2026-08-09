"""
===============================================================================
COSMOS Liquidity Map Engine

Builds a complete institutional liquidity map.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.liquidity.models import (
    LiquidityMap,
    LiquidityObject,
    LiquidityCluster,
)


class LiquidityMapEngine:
    """
    Combines all liquidity information into
    a single institutional map.
    """

    def build(
        self,
        buy_side: list[LiquidityObject],
        sell_side: list[LiquidityObject],
        internal: list[LiquidityObject],
        external: list[LiquidityObject],
        clusters: list[LiquidityCluster],
    ) -> LiquidityMap:

        all_levels = (

            buy_side

            + sell_side

            + internal

            + external

        )

        return LiquidityMap(

            buy_side=buy_side,

            sell_side=sell_side,

            internal=internal,

            external=external,

            clusters=clusters,

            all_levels=all_levels,
        )
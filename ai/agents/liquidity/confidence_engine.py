"""
===============================================================================
COSMOS Liquidity Confidence Engine

Calculates overall liquidity confidence.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.liquidity.constants import (

    WEIGHT_BUY_SIDE,

    WEIGHT_SELL_SIDE,

    WEIGHT_INTERNAL,

    WEIGHT_EXTERNAL,

    WEIGHT_CLUSTER,

    WEIGHT_QUALITY,

)

from ai.agents.liquidity.models import (

    LiquidityMap,

)


class ConfidenceEngine:
    """
    Calculates institutional confidence
    for the Liquidity Agent.
    """

    def calculate(

        self,

        liquidity_map: LiquidityMap,

    ) -> float:

        score = 0.0

        # ---------------------------------------------------------
        # Buy Side
        # ---------------------------------------------------------

        if liquidity_map.buy_side:

            score += WEIGHT_BUY_SIDE

        # ---------------------------------------------------------
        # Sell Side
        # ---------------------------------------------------------

        if liquidity_map.sell_side:

            score += WEIGHT_SELL_SIDE

        # ---------------------------------------------------------
        # Internal
        # ---------------------------------------------------------

        if liquidity_map.internal:

            score += WEIGHT_INTERNAL

        # ---------------------------------------------------------
        # External
        # ---------------------------------------------------------

        if liquidity_map.external:

            score += WEIGHT_EXTERNAL

        # ---------------------------------------------------------
        # Clusters
        # ---------------------------------------------------------

        if liquidity_map.clusters:

            score += WEIGHT_CLUSTER

        # ---------------------------------------------------------
        # Average Quality
        # ---------------------------------------------------------

        if liquidity_map.all_levels:

            average_quality = (

                sum(

                    level.quality

                    for level in liquidity_map.all_levels

                )

                /

                len(liquidity_map.all_levels)

            )

            score += (

                average_quality

                *

                WEIGHT_QUALITY

                /

                100

            )

        return round(

            min(

                score,

                100,

            ),

            2,

        )
"""
===============================================================================
COSMOS Liquidity Cluster Engine

Groups nearby liquidity into institutional clusters.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.liquidity.constants import (
    CLUSTER_DISTANCE,
    MIN_CLUSTER_LEVELS,
)

from ai.agents.liquidity.models import (
    LiquidityObject,
)


class ClusterEngine:
    """
    Groups nearby liquidity levels into
    institutional liquidity clusters.
    """

    def analyze(
        self,
        liquidity: list[LiquidityObject],
    ) -> list[list[LiquidityObject]]:

        if not liquidity:

            return []

        liquidity = sorted(
            liquidity,
            key=lambda x: x.price,
        )

        clusters: list[list[LiquidityObject]] = []

        current_cluster = [

            liquidity[0]

        ]

        for level in liquidity[1:]:

            previous = current_cluster[-1]

            distance = abs(

                level.price

                -

                previous.price

            )

            if distance <= CLUSTER_DISTANCE:

                current_cluster.append(level)

            else:

                if len(current_cluster) >= MIN_CLUSTER_LEVELS:

                    clusters.append(current_cluster)

                current_cluster = [level]

        if len(current_cluster) >= MIN_CLUSTER_LEVELS:

            clusters.append(current_cluster)

        return clusters
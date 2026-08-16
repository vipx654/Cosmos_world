"""
===============================================================================
COSMOS Liquidity Confidence Engine

Advanced Institutional Liquidity Confidence Engine.

Responsibilities:
    • Calculate overall liquidity confidence
    • Evaluate Buy Side coverage
    • Evaluate Sell Side coverage
    • Evaluate Internal liquidity
    • Evaluate External liquidity
    • Evaluate cluster quality
    • Evaluate liquidity quality
    • Evaluate touch density
    • Evaluate strength
    • Evaluate directional balance
    • Prevent score inflation
    • Keep confidence bounded between 0 and 100
    • Preserve backward-compatible public API

Author: COSMOS Development Team
License: MIT
Version: 2.0.0
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
    LiquidityObject,
)


class ConfidenceEngine:
    """
    Calculates institutional confidence for the Liquidity Agent.

    The engine evaluates multiple independent dimensions instead of simply
    checking whether a liquidity category exists.

    Public API remains:

        calculate(liquidity_map) -> float
    """

    ENGINE_NAME = "liquidity_confidence"

    ENGINE_VERSION = "2.0.0"

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def calculate(
        self,
        liquidity_map: LiquidityMap,
    ) -> float:
        """
        Calculate final liquidity confidence.

        Returns:
            float: bounded confidence score from 0 to 100.
        """

        if liquidity_map is None:
            return 0.0

        score = 0.0

        # ---------------------------------------------------------------------
        # Structural coverage
        # ---------------------------------------------------------------------

        score += self._category_score(
            liquidity_map.buy_side,
            WEIGHT_BUY_SIDE,
        )

        score += self._category_score(
            liquidity_map.sell_side,
            WEIGHT_SELL_SIDE,
        )

        score += self._category_score(
            liquidity_map.internal,
            WEIGHT_INTERNAL,
        )

        score += self._category_score(
            liquidity_map.external,
            WEIGHT_EXTERNAL,
        )

        # ---------------------------------------------------------------------
        # Cluster intelligence
        # ---------------------------------------------------------------------

        score += self._cluster_score(
            liquidity_map
        )

        # ---------------------------------------------------------------------
        # Overall liquidity quality
        # ---------------------------------------------------------------------

        score += self._quality_score(
            liquidity_map.all_levels
        )

        # ---------------------------------------------------------------------
        # Additional structural intelligence.
        #
        # These bonuses are deliberately capped so the confidence cannot
        # exceed 100 simply because many liquidity objects were detected.
        # ---------------------------------------------------------------------

        score += self._density_bonus(
            liquidity_map.all_levels
        )

        score += self._touch_bonus(
            liquidity_map.all_levels
        )

        score += self._directional_balance_bonus(
            liquidity_map
        )

        return self._bound(
            score
        )

    # =========================================================================
    # CATEGORY SCORE
    # =========================================================================

    @staticmethod
    def _category_score(
        levels: list[LiquidityObject],
        weight: float,
    ) -> float:
        """
        Score a liquidity category.

        A category receives stronger confidence when it contains multiple
        high-quality levels rather than receiving the entire weight merely
        because one object exists.
        """

        if not levels:
            return 0.0

        count_factor = min(
            len(levels) / 3.0,
            1.0,
        )

        quality = ConfidenceEngine._average_quality(
            levels
        )

        quality_factor = quality / 100.0

        # Preserve the original category weight while making the result
        # sensitive to actual evidence.
        factor = (
            0.45
            + (
                0.55
                * max(
                    count_factor,
                    quality_factor,
                )
            )
        )

        return weight * factor

    # =========================================================================
    # CLUSTER SCORE
    # =========================================================================

    @staticmethod
    def _cluster_score(
        liquidity_map: LiquidityMap,
    ) -> float:
        """
        Evaluate institutional liquidity clusters.

        Strong clusters with high confidence and meaningful member counts
        receive more weight.
        """

        clusters = liquidity_map.clusters

        if not clusters:
            return 0.0

        base_weight = float(
            WEIGHT_CLUSTER
        )

        average_strength = (
            sum(
                max(
                    0.0,
                    min(
                        float(
                            cluster.combined_strength
                        ),
                        100.0,
                    ),
                )
                for cluster in clusters
            )
            / len(clusters)
        )

        average_confidence = (
            sum(
                max(
                    0.0,
                    min(
                        float(
                            cluster.combined_confidence
                        ),
                        100.0,
                    ),
                )
                for cluster in clusters
            )
            / len(clusters)
        )

        average_members = (
            sum(
                max(
                    int(
                        cluster.liquidity_count
                    ),
                    0,
                )
                for cluster in clusters
            )
            / len(clusters)
        )

        strength_factor = (
            average_strength
            / 100.0
        )

        confidence_factor = (
            average_confidence
            / 100.0
        )

        density_factor = min(
            average_members / 4.0,
            1.0,
        )

        factor = (
            0.35
            + (
                0.25
                * strength_factor
            )
            + (
                0.25
                * confidence_factor
            )
            + (
                0.15
                * density_factor
            )
        )

        return min(
            base_weight * factor,
            base_weight,
        )

    # =========================================================================
    # QUALITY SCORE
    # =========================================================================

    @staticmethod
    def _quality_score(
        levels: list[LiquidityObject],
    ) -> float:
        """
        Evaluate average liquidity quality.
        """

        if not levels:
            return 0.0

        average_quality = (
            ConfidenceEngine._average_quality(
                levels
            )
        )

        return (
            average_quality
            * float(WEIGHT_QUALITY)
            / 100.0
        )

    # =========================================================================
    # DENSITY BONUS
    # =========================================================================

    @staticmethod
    def _density_bonus(
        levels: list[LiquidityObject],
    ) -> float:
        """
        Reward meaningful liquidity density.

        This is intentionally capped.
        """

        if not levels:
            return 0.0

        count = len(
            levels
        )

        if count <= 1:
            return 0.0

        return min(
            (
                count - 1
            )
            * 0.75,
            4.0,
        )

    # =========================================================================
    # TOUCH BONUS
    # =========================================================================

    @staticmethod
    def _touch_bonus(
        levels: list[LiquidityObject],
    ) -> float:
        """
        Reward repeated interaction with liquidity levels.

        Multiple touches can indicate stronger structural relevance.
        """

        if not levels:
            return 0.0

        average_touches = (
            sum(
                max(
                    int(level.touches),
                    0,
                )
                for level in levels
            )
            / len(levels)
        )

        if average_touches <= 1:
            return 0.0

        return min(
            (
                average_touches
                - 1.0
            )
            * 1.5,
            5.0,
        )

    # =========================================================================
    # DIRECTIONAL BALANCE
    # =========================================================================

    @staticmethod
    def _directional_balance_bonus(
        liquidity_map: LiquidityMap,
    ) -> float:
        """
        Evaluate whether both external liquidity directions are represented.

        Balanced Buy/Sell liquidity generally provides stronger structural
        context than a map containing only one side.
        """

        buy_count = len(
            liquidity_map.buy_side
        )

        sell_count = len(
            liquidity_map.sell_side
        )

        if (
            buy_count == 0
            or sell_count == 0
        ):
            return 0.0

        total = (
            buy_count
            + sell_count
        )

        if total <= 0:
            return 0.0

        balance = (
            min(
                buy_count,
                sell_count,
            )
            /
            max(
                buy_count,
                sell_count,
            )
        )

        return min(
            balance * 3.0,
            3.0,
        )

    # =========================================================================
    # AVERAGE QUALITY
    # =========================================================================

    @staticmethod
    def _average_quality(
        levels: list[LiquidityObject],
    ) -> float:
        """
        Calculate bounded average quality.
        """

        if not levels:
            return 0.0

        values = [
            max(
                0.0,
                min(
                    float(
                        level.quality
                    ),
                    100.0,
                ),
            )
            for level in levels
        ]

        return (
            sum(values)
            / len(values)
        )

    # =========================================================================
    # FINAL BOUND
    # =========================================================================

    @staticmethod
    def _bound(
        score: float,
    ) -> float:
        """
        Guarantee a valid confidence range.
        """

        return round(
            max(
                0.0,
                min(
                    float(score),
                    100.0,
                ),
            ),
            2,
        )
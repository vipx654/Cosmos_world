"""
===============================================================================
COSMOS Liquidity Cluster Engine

Advanced Institutional Liquidity Clustering Engine.

Responsibilities:
    • Group nearby liquidity levels
    • Detect dense liquidity zones
    • Support adaptive cluster distance
    • Calculate cluster density
    • Calculate combined strength
    • Calculate combined confidence
    • Estimate sweep probability
    • Preserve liquidity diversity
    • Rank cluster significance
    • Generate deterministic cluster groups
    • Maintain backward compatibility with the existing LiquidityMap
      and downstream engines

Author: COSMOS Development Team
License: MIT
Version: 2.0.0
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict

from ai.agents.liquidity.constants import (
    CLUSTER_DISTANCE,
    MIN_CLUSTER_LEVELS,
)

from ai.agents.liquidity.models import (
    LiquidityObject,
    LiquidityType,
)


# =============================================================================
# ENGINE
# =============================================================================


class ClusterEngine:
    """
    Advanced Institutional Liquidity Cluster Engine.

    A cluster represents a concentrated region containing multiple
    liquidity levels.

    Pipeline:

        Liquidity Levels
              ↓
        Price Normalization
              ↓
        Adaptive Distance
              ↓
        Density Detection
              ↓
        Cluster Formation
              ↓
        Cluster Scoring
              ↓
        Significance Ranking
    """

    ENGINE_NAME = "cluster"

    ENGINE_VERSION = "2.0.0"

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        liquidity: list[LiquidityObject],
    ) -> list[list[LiquidityObject]]:
        """
        Group nearby liquidity levels.

        The return type intentionally remains:

            list[list[LiquidityObject]]

        because existing downstream COSMOS components already consume
        clusters in this format.
        """

        if not liquidity:
            return []

        # ---------------------------------------------------------------------
        # Remove invalid levels.
        # ---------------------------------------------------------------------

        valid_levels = [
            level
            for level in liquidity
            if self._is_valid_level(level)
        ]

        if not valid_levels:
            return []

        # ---------------------------------------------------------------------
        # Sort by price.
        # ---------------------------------------------------------------------

        ordered = sorted(
            valid_levels,
            key=lambda level: (
                level.price,
                level.liquidity_type.value,
            ),
        )

        # ---------------------------------------------------------------------
        # Build adaptive clusters.
        # ---------------------------------------------------------------------

        raw_clusters = self._build_clusters(
            ordered
        )

        # ---------------------------------------------------------------------
        # Enforce minimum cluster size.
        # ---------------------------------------------------------------------

        clusters = [
            cluster
            for cluster in raw_clusters
            if len(cluster) >= MIN_CLUSTER_LEVELS
        ]

        if not clusters:
            return []

        # ---------------------------------------------------------------------
        # Score every cluster.
        #
        # Scores are attached to each member through evidence/metadata-free
        # existing model compatibility. We deliberately do not alter the
        # LiquidityObject schema here.
        # ---------------------------------------------------------------------

        scored = []

        for cluster in clusters:

            self._evaluate_cluster(
                cluster
            )

            scored.append(
                cluster
            )

        # ---------------------------------------------------------------------
        # Rank clusters.
        # ---------------------------------------------------------------------

        scored.sort(
            key=self._cluster_rank,
            reverse=True,
        )

        return scored

    # =========================================================================
    # CLUSTER BUILDING
    # =========================================================================

    def _build_clusters(
        self,
        liquidity: list[LiquidityObject],
    ) -> list[list[LiquidityObject]]:
        """
        Build price-proximity clusters.

        Unlike the original implementation, the engine considers the
        current cluster's price span instead of blindly comparing only
        adjacent levels.
        """

        if not liquidity:
            return []

        clusters: list[list[LiquidityObject]] = []

        current: list[LiquidityObject] = [
            liquidity[0]
        ]

        for level in liquidity[1:]:

            if self._belongs_to_cluster(
                current,
                level,
            ):

                current.append(level)

            else:

                clusters.append(
                    current
                )

                current = [
                    level
                ]

        if current:
            clusters.append(
                current
            )

        return clusters

    # =========================================================================
    # CLUSTER MEMBERSHIP
    # =========================================================================

    def _belongs_to_cluster(
        self,
        cluster: list[LiquidityObject],
        level: LiquidityObject,
    ) -> bool:
        """
        Determine whether a liquidity level belongs to the current cluster.
        """

        if not cluster:
            return True

        prices = [
            member.price
            for member in cluster
        ]

        lower = min(
            prices
        )

        upper = max(
            prices
        )

        # ---------------------------------------------------------------------
        # Distance from the existing cluster boundaries.
        # ---------------------------------------------------------------------

        distance_to_lower = abs(
            level.price
            - lower
        )

        distance_to_upper = abs(
            level.price
            - upper
        )

        if min(
            distance_to_lower,
            distance_to_upper,
        ) <= CLUSTER_DISTANCE:

            return True

        # ---------------------------------------------------------------------
        # Cluster midpoint check.
        #
        # This allows dense zones to remain together even when the new level
        # is slightly farther from one boundary but still lies inside the
        # overall institutional zone.
        # ---------------------------------------------------------------------

        midpoint = (
            lower
            + upper
        ) / 2.0

        if (
            lower
            <= level.price
            <= upper
            and
            abs(
                level.price
                - midpoint
            )
            <= CLUSTER_DISTANCE
        ):

            return True

        return False

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def _is_valid_level(
        self,
        level: LiquidityObject,
    ) -> bool:
        """
        Validate a liquidity level before clustering.
        """

        if level is None:
            return False

        try:

            price = float(
                level.price
            )

        except (
            TypeError,
            ValueError,
        ):

            return False

        if not price == price:
            return False

        if price in (
            float("inf"),
            float("-inf"),
        ):

            return False

        return True

    # =========================================================================
    # CLUSTER EVALUATION
    # =========================================================================

    def _evaluate_cluster(
        self,
        cluster: list[LiquidityObject],
    ) -> None:
        """
        Evaluate a cluster and enrich member evidence.

        The existing LiquidityObject schema intentionally remains untouched,
        so this method stores explainability information inside the existing
        evidence field.
        """

        if not cluster:
            return

        center = self._center_price(
            cluster
        )

        density = self._density(
            cluster
        )

        combined_strength = (
            self._combined_strength(
                cluster
            )
        )

        combined_confidence = (
            self._combined_confidence(
                cluster
            )
        )

        sweep_probability = (
            self._sweep_probability(
                cluster,
                density=density,
            )
        )

        liquidity_types = {
            level.liquidity_type
            for level in cluster
        }

        type_count = len(
            liquidity_types
        )

        # ---------------------------------------------------------------------
        # Add cluster evidence without changing public models.
        # ---------------------------------------------------------------------

        for level in cluster:

            evidence = list(
                level.evidence
            )

            evidence.append(
                (
                    f"Cluster center: "
                    f"{center:.10f}"
                )
            )

            evidence.append(
                (
                    f"Cluster density: "
                    f"{density:.2f}"
                )
            )

            evidence.append(
                (
                    f"Combined strength: "
                    f"{combined_strength:.2f}"
                )
            )

            evidence.append(
                (
                    f"Combined confidence: "
                    f"{combined_confidence:.2f}"
                )
            )

            evidence.append(
                (
                    f"Estimated sweep probability: "
                    f"{sweep_probability:.2f}"
                )
            )

            if type_count >= 2:

                evidence.append(
                    "Multi-type liquidity cluster"
                )

            level.evidence = self._unique_evidence(
                evidence
            )

    # =========================================================================
    # CENTER PRICE
    # =========================================================================

    def _center_price(
        self,
        cluster: list[LiquidityObject],
    ) -> float:
        """
        Calculate liquidity-weighted cluster center.
        """

        if not cluster:
            return 0.0

        weighted_price = 0.0
        total_weight = 0.0

        for level in cluster:

            weight = max(
                float(level.strength),
                1.0,
            )

            weighted_price += (
                level.price
                * weight
            )

            total_weight += weight

        if total_weight <= 0:
            return cluster[0].price

        return (
            weighted_price
            / total_weight
        )

    # =========================================================================
    # DENSITY
    # =========================================================================

    def _density(
        self,
        cluster: list[LiquidityObject],
    ) -> float:
        """
        Calculate cluster density.

        Higher density means more liquidity concentrated inside a smaller
        price region.
        """

        if not cluster:
            return 0.0

        if len(cluster) == 1:
            return 0.0

        prices = [
            level.price
            for level in cluster
        ]

        spread = (
            max(prices)
            - min(prices)
        )

        if spread <= 0:
            return 100.0

        density = (
            len(cluster)
            / spread
        )

        # ---------------------------------------------------------------------
        # Normalize density against the configured cluster distance.
        # ---------------------------------------------------------------------

        normalized = (
            density
            * CLUSTER_DISTANCE
        )

        return round(
            min(
                normalized
                * 100.0,
                100.0,
            ),
            2,
        )

    # =========================================================================
    # COMBINED STRENGTH
    # =========================================================================

    def _combined_strength(
        self,
        cluster: list[LiquidityObject],
    ) -> float:
        """
        Calculate combined cluster strength.
        """

        if not cluster:
            return 0.0

        strengths = [
            max(
                0.0,
                min(
                    float(level.strength),
                    100.0,
                ),
            )
            for level in cluster
        ]

        # ---------------------------------------------------------------------
        # Root-mean-square style aggregation gives stronger levels more
        # influence without allowing the number of levels alone to exceed 100.
        # ---------------------------------------------------------------------

        weighted = sum(
            strength * strength
            for strength in strengths
        )

        score = (
            weighted
            / len(strengths)
        ) ** 0.5

        # Additional density bonus.
        density_bonus = min(
            len(cluster) * 2.0,
            10.0,
        )

        return round(
            min(
                score
                + density_bonus,
                100.0,
            ),
            2,
        )

    # =========================================================================
    # COMBINED CONFIDENCE
    # =========================================================================

    def _combined_confidence(
        self,
        cluster: list[LiquidityObject],
    ) -> float:
        """
        Calculate combined confidence.
        """

        if not cluster:
            return 0.0

        confidences = [
            max(
                0.0,
                min(
                    float(level.confidence),
                    100.0,
                ),
            )
            for level in cluster
        ]

        average = (
            sum(confidences)
            / len(confidences)
        )

        diversity = len(
            {
                level.liquidity_type
                for level in cluster
            }
        )

        diversity_bonus = min(
            diversity * 4.0,
            12.0,
        )

        size_bonus = min(
            len(cluster) * 2.0,
            10.0,
        )

        return round(
            min(
                average
                + diversity_bonus
                + size_bonus,
                100.0,
            ),
            2,
        )

    # =========================================================================
    # SWEEP PROBABILITY
    # =========================================================================

    def _sweep_probability(
        self,
        cluster: list[LiquidityObject],
        density: float,
    ) -> float:
        """
        Estimate the probability that the concentrated liquidity zone
        becomes a sweep target.

        This is a structural probability estimate, not a trading signal.
        """

        if not cluster:
            return 0.0

        average_confidence = (
            sum(
                float(level.confidence)
                for level in cluster
            )
            / len(cluster)
        )

        average_strength = (
            sum(
                float(level.strength)
                for level in cluster
            )
            / len(cluster)
        )

        touch_score = min(
            len(cluster)
            * 8.0,
            20.0,
        )

        probability = (
            average_confidence
            * 0.35
            +
            average_strength
            * 0.35
            +
            density
            * 0.20
            +
            touch_score
            * 0.50
        )

        return round(
            max(
                0.0,
                min(
                    probability,
                    100.0,
                ),
            ),
            2,
        )

    # =========================================================================
    # RANKING
    # =========================================================================

    def _cluster_rank(
        self,
        cluster: list[LiquidityObject],
    ) -> tuple:
        """
        Rank clusters by institutional significance.
        """

        if not cluster:
            return (
                0.0,
                0.0,
                0,
            )

        combined_strength = (
            self._combined_strength(
                cluster
            )
        )

        combined_confidence = (
            self._combined_confidence(
                cluster
            )
        )

        return (
            combined_strength
            + combined_confidence,
            len(cluster),
            len(
                {
                    level.liquidity_type
                    for level in cluster
                }
            ),
        )

    # =========================================================================
    # EVIDENCE DEDUPLICATION
    # =========================================================================

    def _unique_evidence(
        self,
        evidence: list[str],
    ) -> list[str]:
        """
        Preserve evidence order while removing duplicates.
        """

        seen: set[str] = set()

        result: list[str] = []

        for item in evidence:

            if item in seen:
                continue

            seen.add(
                item
            )

            result.append(
                item
            )

        return result
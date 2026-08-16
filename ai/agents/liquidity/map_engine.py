"""
===============================================================================
COSMOS Liquidity Map Engine

Advanced Institutional Liquidity Map Builder.

Responsibilities:
    • Combine Buy Side Liquidity
    • Combine Sell Side Liquidity
    • Combine Internal Liquidity
    • Combine External Liquidity
    • Normalize liquidity levels
    • Remove duplicate liquidity objects
    • Build institutional liquidity clusters
    • Calculate cluster center
    • Calculate cluster boundaries
    • Calculate combined strength
    • Calculate combined confidence
    • Estimate sweep probability
    • Preserve deterministic ordering
    • Produce a complete LiquidityMap
    • Maintain backward compatibility with existing COSMOS agents

Pipeline:

    Buy Side ─────┐
    Sell Side ────┤
    Internal ─────┼──→ Liquidity Map
    External ─────┤
    Clusters ─────┘

Author: COSMOS Development Team
License: MIT
Version: 2.0.0
===============================================================================
"""

from __future__ import annotations

from hashlib import sha1

from ai.agents.liquidity.models import (
    LiquidityCluster,
    LiquidityMap,
    LiquidityObject,
)


# =============================================================================
# ENGINE
# =============================================================================


class LiquidityMapEngine:
    """
    Advanced institutional liquidity map builder.

    The engine combines all upstream liquidity discoveries into one
    deterministic market-wide liquidity map.
    """

    ENGINE_NAME = "liquidity_map"

    ENGINE_VERSION = "2.0.0"

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def build(
        self,
        buy_side: list[LiquidityObject],
        sell_side: list[LiquidityObject],
        internal: list[LiquidityObject],
        external: list[LiquidityObject],
        clusters: list[
            LiquidityCluster
            | list[LiquidityObject]
        ],
    ) -> LiquidityMap:
        """
        Build the complete institutional liquidity map.

        Existing callers can continue passing:

            list[LiquidityCluster]

        while legacy cluster output:

            list[list[LiquidityObject]]

        is also accepted.
        """

        # ---------------------------------------------------------------------
        # Defensive normalization.
        # ---------------------------------------------------------------------

        buy_side = self._clean_levels(
            buy_side
        )

        sell_side = self._clean_levels(
            sell_side
        )

        internal = self._clean_levels(
            internal
        )

        external = self._clean_levels(
            external
        )

        # ---------------------------------------------------------------------
        # Combine every liquidity source.
        # ---------------------------------------------------------------------

        all_levels = self._combine_levels(
            buy_side,
            sell_side,
            internal,
            external,
        )

        # ---------------------------------------------------------------------
        # Normalize clusters.
        # ---------------------------------------------------------------------

        normalized_clusters = (
            self._normalize_clusters(
                clusters
            )
        )

        # ---------------------------------------------------------------------
        # Ensure cluster members are reflected in the global level map.
        # ---------------------------------------------------------------------

        all_levels = self._merge_cluster_members(
            all_levels,
            normalized_clusters,
        )

        # ---------------------------------------------------------------------
        # Deterministic ordering.
        # ---------------------------------------------------------------------

        all_levels.sort(
            key=lambda level: (
                level.price,
                level.liquidity_type.value,
            )
        )

        normalized_clusters.sort(
            key=lambda cluster: (
                cluster.center_price,
                cluster.id,
            )
        )

        return LiquidityMap(
            buy_side=buy_side,
            sell_side=sell_side,
            internal=internal,
            external=external,
            clusters=normalized_clusters,
            all_levels=all_levels,
        )

    # =========================================================================
    # LEVEL NORMALIZATION
    # =========================================================================

    def _clean_levels(
        self,
        levels: list[LiquidityObject],
    ) -> list[LiquidityObject]:
        """
        Remove invalid levels and deterministic duplicates.
        """

        if not levels:
            return []

        cleaned: list[LiquidityObject] = []

        seen: set[tuple] = set()

        for level in levels:

            if not self._valid_level(
                level
            ):
                continue

            key = (
                level.liquidity_type,
                round(
                    float(level.price),
                    10,
                ),
                level.status,
            )

            if key in seen:

                self._merge_duplicate_into_existing(
                    cleaned,
                    level,
                )

                continue

            seen.add(
                key
            )

            cleaned.append(
                level
            )

        return cleaned

    # =========================================================================
    # LEVEL VALIDATION
    # =========================================================================

    @staticmethod
    def _valid_level(
        level: LiquidityObject | None,
    ) -> bool:
        """
        Validate a liquidity object.
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

        if price != price:
            return False

        if price in (
            float("inf"),
            float("-inf"),
        ):
            return False

        return True

    # =========================================================================
    # COMBINE LEVELS
    # =========================================================================

    def _combine_levels(
        self,
        buy_side: list[LiquidityObject],
        sell_side: list[LiquidityObject],
        internal: list[LiquidityObject],
        external: list[LiquidityObject],
    ) -> list[LiquidityObject]:
        """
        Combine all liquidity categories.

        Duplicate levels are merged rather than silently discarded.
        """

        result: list[LiquidityObject] = []

        for source in (
            buy_side,
            sell_side,
            internal,
            external,
        ):

            for level in source:

                if not self._merge_duplicate_into_existing(
                    result,
                    level,
                ):

                    result.append(
                        level
                    )

        return result

    # =========================================================================
    # DUPLICATE MERGING
    # =========================================================================

    def _merge_duplicate_into_existing(
        self,
        levels: list[LiquidityObject],
        incoming: LiquidityObject,
    ) -> bool:
        """
        Merge an equivalent liquidity level.

        Returns:

            True  → merged
            False → no matching level
        """

        for existing in levels:

            if not self._same_level(
                existing,
                incoming,
            ):
                continue

            # -----------------------------------------------------------------
            # Preserve the strongest observed values.
            # -----------------------------------------------------------------

            existing.touches = max(
                int(existing.touches),
                int(incoming.touches),
            )

            existing.strength = max(
                float(existing.strength),
                float(incoming.strength),
            )

            existing.confidence = max(
                float(existing.confidence),
                float(incoming.confidence),
            )

            existing.quality = max(
                float(existing.quality),
                float(incoming.quality),
            )

            existing.age = min(
                int(existing.age),
                int(incoming.age),
            )

            # -----------------------------------------------------------------
            # Preserve closest distance.
            # -----------------------------------------------------------------

            if abs(
                float(incoming.distance)
            ) < abs(
                float(existing.distance)
            ):

                existing.distance = (
                    incoming.distance
                )

            # -----------------------------------------------------------------
            # Preserve source information.
            # -----------------------------------------------------------------

            if (
                incoming.source
                and
                incoming.source
                != existing.source
            ):

                sources = [
                    item.strip()
                    for item in (
                        f"{existing.source},"
                        f"{incoming.source}"
                    ).split(",")
                    if item.strip()
                ]

                existing.source = ",".join(
                    dict.fromkeys(
                        sources
                    )
                )

            # -----------------------------------------------------------------
            # Merge evidence.
            # -----------------------------------------------------------------

            existing.evidence = (
                self._unique_strings(
                    existing.evidence
                    + incoming.evidence
                )
            )

            return True

        return False

    # =========================================================================
    # SAME LEVEL
    # =========================================================================

    @staticmethod
    def _same_level(
        first: LiquidityObject,
        second: LiquidityObject,
    ) -> bool:
        """
        Determine whether two objects represent the same liquidity level.
        """

        return (
            first.liquidity_type
            == second.liquidity_type
            and
            first.status
            == second.status
            and
            round(
                float(first.price),
                10,
            )
            ==
            round(
                float(second.price),
                10,
            )
        )

    # =========================================================================
    # CLUSTER NORMALIZATION
    # =========================================================================

    def _normalize_clusters(
        self,
        clusters: list[
            LiquidityCluster
            | list[LiquidityObject]
        ],
    ) -> list[LiquidityCluster]:
        """
        Convert both modern LiquidityCluster objects and legacy
        list-of-level clusters into a consistent representation.
        """

        if not clusters:
            return []

        normalized: list[LiquidityCluster] = []

        for cluster in clusters:

            if isinstance(
                cluster,
                LiquidityCluster,
            ):

                normalized.append(
                    cluster
                )

                continue

            if isinstance(
                cluster,
                list,
            ):

                members = [
                    level
                    for level in cluster
                    if self._valid_level(
                        level
                    )
                ]

                if len(members) < 1:
                    continue

                normalized.append(
                    self._create_cluster(
                        members
                    )
                )

        return normalized

    # =========================================================================
    # CREATE CLUSTER
    # =========================================================================

    def _create_cluster(
        self,
        members: list[LiquidityObject],
    ) -> LiquidityCluster:
        """
        Convert a legacy cluster into a full LiquidityCluster.
        """

        prices = [
            float(level.price)
            for level in members
        ]

        lower = min(
            prices
        )

        upper = max(
            prices
        )

        center = self._weighted_center(
            members
        )

        strength = self._combined_strength(
            members
        )

        confidence = self._combined_confidence(
            members
        )

        sweep_probability = (
            self._sweep_probability(
                members
            )
        )

        cluster_id = self._cluster_id(
            members,
            center,
        )

        return LiquidityCluster(
            id=cluster_id,
            center_price=round(
                center,
                10,
            ),
            upper_price=round(
                upper,
                10,
            ),
            lower_price=round(
                lower,
                10,
            ),
            liquidity_count=len(
                members
            ),
            combined_strength=round(
                strength,
                2,
            ),
            combined_confidence=round(
                confidence,
                2,
            ),
            expected_sweep_probability=round(
                sweep_probability,
                2,
            ),
            members=list(
                members
            ),
        )

    # =========================================================================
    # WEIGHTED CENTER
    # =========================================================================

    @staticmethod
    def _weighted_center(
        members: list[LiquidityObject],
    ) -> float:
        """
        Calculate strength-weighted cluster center.
        """

        if not members:
            return 0.0

        numerator = 0.0

        denominator = 0.0

        for level in members:

            weight = max(
                float(level.strength),
                1.0,
            )

            numerator += (
                float(level.price)
                * weight
            )

            denominator += weight

        if denominator <= 0:
            return float(
                members[0].price
            )

        return (
            numerator
            / denominator
        )

    # =========================================================================
    # COMBINED STRENGTH
    # =========================================================================

    @staticmethod
    def _combined_strength(
        members: list[LiquidityObject],
    ) -> float:
        """
        Calculate combined cluster strength.
        """

        if not members:
            return 0.0

        values = [
            max(
                0.0,
                min(
                    float(level.strength),
                    100.0,
                ),
            )
            for level in members
        ]

        average = (
            sum(values)
            / len(values)
        )

        size_bonus = min(
            len(members) * 2.5,
            15.0,
        )

        return min(
            average
            + size_bonus,
            100.0,
        )

    # =========================================================================
    # COMBINED CONFIDENCE
    # =========================================================================

    @staticmethod
    def _combined_confidence(
        members: list[LiquidityObject],
    ) -> float:
        """
        Calculate combined cluster confidence.
        """

        if not members:
            return 0.0

        values = [
            max(
                0.0,
                min(
                    float(level.confidence),
                    100.0,
                ),
            )
            for level in members
        ]

        average = (
            sum(values)
            / len(values)
        )

        diversity = len(
            {
                level.liquidity_type
                for level in members
            }
        )

        diversity_bonus = min(
            diversity * 5.0,
            15.0,
        )

        return min(
            average
            + diversity_bonus,
            100.0,
        )

    # =========================================================================
    # SWEEP PROBABILITY
    # =========================================================================

    @staticmethod
    def _sweep_probability(
        members: list[LiquidityObject],
    ) -> float:
        """
        Estimate structural probability of the cluster becoming a sweep
        target.

        This is an analytical metric, not an execution signal.
        """

        if not members:
            return 0.0

        average_strength = (
            sum(
                float(level.strength)
                for level in members
            )
            / len(members)
        )

        average_confidence = (
            sum(
                float(level.confidence)
                for level in members
            )
            / len(members)
        )

        touch_factor = min(
            sum(
                max(
                    int(level.touches),
                    0,
                )
                for level in members
            )
            * 5.0,
            25.0,
        )

        probability = (
            average_strength
            * 0.35
            +
            average_confidence
            * 0.35
            +
            touch_factor
            * 0.60
        )

        return max(
            0.0,
            min(
                probability,
                100.0,
            ),
        )

    # =========================================================================
    # CLUSTER ID
    # =========================================================================

    @staticmethod
    def _cluster_id(
        members: list[LiquidityObject],
        center: float,
    ) -> str:
        """
        Generate a deterministic cluster identifier.
        """

        payload = "|".join(
            sorted(
                (
                    f"{level.liquidity_type.value}:"
                    f"{level.price:.10f}:"
                    f"{level.status.value}"
                )
                for level in members
            )
        )

        payload += (
            f"|{center:.10f}"
        )

        digest = sha1(
            payload.encode(
                "utf-8"
            )
        ).hexdigest()[:16]

        return (
            f"liq-cluster-{digest}"
        )

    # =========================================================================
    # MERGE CLUSTER MEMBERS
    # =========================================================================

    def _merge_cluster_members(
        self,
        levels: list[LiquidityObject],
        clusters: list[LiquidityCluster],
    ) -> list[LiquidityObject]:
        """
        Ensure cluster members are represented in all_levels.
        """

        result = list(
            levels
        )

        for cluster in clusters:

            for member in cluster.members:

                if not self._merge_duplicate_into_existing(
                    result,
                    member,
                ):

                    result.append(
                        member
                    )

        return result

    # =========================================================================
    # STRING DEDUPLICATION
    # =========================================================================

    @staticmethod
    def _unique_strings(
        values: list[str],
    ) -> list[str]:
        """
        Deduplicate strings while preserving order.
        """

        result: list[str] = []

        seen: set[str] = set()

        for value in values:

            if not value:
                continue

            if value in seen:
                continue

            seen.add(
                value
            )

            result.append(
                value
            )

        return result
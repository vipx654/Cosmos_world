"""
===============================================================================
COSMOS Internal Liquidity Engine

Advanced Institutional Internal Liquidity Detection.

Responsibilities:
    • Detect internal liquidity between structural boundaries
    • Identify internal swing highs and lows
    • Measure liquidity age
    • Calculate structural strength
    • Calculate detection confidence
    • Measure distance from external boundaries
    • Generate explainable evidence
    • Preserve deterministic output
    • Prevent duplicate internal liquidity levels
    • Rank internal liquidity by significance

Author: COSMOS Development Team
License: MIT
Version: 2.0.0
===============================================================================
"""

from __future__ import annotations

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.liquidity.constants import (
    LIQUIDITY_TOLERANCE,
    MAX_AGE,
    MAX_TOUCHES,
)

from ai.agents.liquidity.models import (
    LiquidityObject,
    LiquidityStatus,
    LiquidityType,
)


# =============================================================================
# ENGINE
# =============================================================================


class InternalLiquidityEngine:
    """
    Advanced Internal Liquidity Engine.

    Internal liquidity represents liquidity that exists inside the
    active structural range.

    Instead of blindly treating every middle swing equally, the engine
    evaluates:

        • structural position
        • swing type
        • distance from boundaries
        • age
        • local repetition
        • price alignment
        • strength
        • confidence
        • evidence

    Detection pipeline:

        Swing Structure
            ↓
        External Boundaries
            ↓
        Internal Swing Extraction
            ↓
        Local Liquidity Analysis
            ↓
        Strength
            ↓
        Confidence
            ↓
        Distance
            ↓
        Age
            ↓
        Evidence
            ↓
        LiquidityObject
    """

    ENGINE_NAME = "internal"

    ENGINE_VERSION = "2.0.0"

    LIQUIDITY_SOURCE = "internal_structure"

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> list[LiquidityObject]:
        """
        Analyze swing points and detect Internal Liquidity.

        Parameters
        ----------
        swings:
            Ordered structural swing points.

        Returns
        -------
        list[LiquidityObject]
            Internal liquidity levels.
        """

        if len(swings) < 4:
            return []

        # ---------------------------------------------------------------------
        # Normalize ordering.
        #
        # Market Structure normally provides chronological swings, but sorting
        # here makes this engine deterministic even when callers provide
        # unordered data.
        # ---------------------------------------------------------------------

        ordered_swings = sorted(
            swings,
            key=lambda swing: swing.index,
        )

        if len(ordered_swings) < 4:
            return []

        # ---------------------------------------------------------------------
        # Determine structural boundaries.
        # ---------------------------------------------------------------------

        external_high = max(
            ordered_swings,
            key=lambda swing: swing.price,
        )

        external_low = min(
            ordered_swings,
            key=lambda swing: swing.price,
        )

        upper_boundary = external_high.price

        lower_boundary = external_low.price

        # ---------------------------------------------------------------------
        # Invalid range protection.
        # ---------------------------------------------------------------------

        if upper_boundary <= lower_boundary:
            return []

        # ---------------------------------------------------------------------
        # Everything inside the external boundaries is internal.
        # ---------------------------------------------------------------------

        internal_swings = [
            swing
            for swing in ordered_swings
            if (
                lower_boundary
                < swing.price
                < upper_boundary
            )
        ]

        if not internal_swings:
            return []

        latest_index = max(
            swing.index
            for swing in ordered_swings
        )

        liquidity: list[LiquidityObject] = []

        # ---------------------------------------------------------------------
        # Create an internal liquidity object for each structural swing.
        # ---------------------------------------------------------------------

        for swing in internal_swings:

            touches = self._count_nearby_touches(
                swing,
                internal_swings,
            )

            touches = min(
                max(touches, 1),
                MAX_TOUCHES,
            )

            distance = self._calculate_boundary_distance(
                swing.price,
                lower_boundary,
                upper_boundary,
            )

            age = max(
                latest_index
                - swing.index,
                0,
            )

            age = min(
                age,
                MAX_AGE,
            )

            dispersion = self._calculate_local_dispersion(
                swing,
                internal_swings,
            )

            strength = self._calculate_strength(
                swing_type=swing.swing_type,
                touches=touches,
                distance=distance,
                dispersion=dispersion,
            )

            confidence = self._calculate_confidence(
                touches=touches,
                distance=distance,
                dispersion=dispersion,
                age=age,
            )

            evidence = self._build_evidence(
                swing=swing,
                touches=touches,
                distance=distance,
                dispersion=dispersion,
                age=age,
            )

            liquidity.append(
                LiquidityObject(
                    liquidity_type=LiquidityType.INTERNAL,

                    status=LiquidityStatus.UNTOUCHED,

                    price=round(
                        swing.price,
                        10,
                    ),

                    touches=touches,

                    strength=strength,

                    confidence=confidence,

                    quality=0.0,

                    age=age,

                    distance=round(
                        distance,
                        10,
                    ),

                    source=self.LIQUIDITY_SOURCE,

                    evidence=evidence,
                )
            )

        # ---------------------------------------------------------------------
        # Remove duplicate levels.
        # ---------------------------------------------------------------------

        liquidity = self._deduplicate(
            liquidity
        )

        # ---------------------------------------------------------------------
        # Strongest internal liquidity first.
        # ---------------------------------------------------------------------

        liquidity.sort(
            key=lambda level: (
                level.confidence,
                level.strength,
                level.touches,
                -level.age,
            ),
            reverse=True,
        )

        return liquidity

    # =========================================================================
    # TOUCH ANALYSIS
    # =========================================================================

    def _count_nearby_touches(
        self,
        target: SwingPoint,
        swings: list[SwingPoint],
    ) -> int:
        """
        Count nearby structural touches around a swing price.

        Both highs and lows can contribute to an internal structural level.
        """

        touches = 0

        for swing in swings:

            if abs(
                swing.price
                - target.price
            ) <= LIQUIDITY_TOLERANCE:

                touches += 1

        return touches

    # =========================================================================
    # BOUNDARY DISTANCE
    # =========================================================================

    def _calculate_boundary_distance(
        self,
        price: float,
        lower_boundary: float,
        upper_boundary: float,
    ) -> float:
        """
        Calculate normalized distance from the nearest external boundary.

        A value near 0 means the level is close to an external boundary.
        A value near 0.5 means the level is near the middle of the range.
        """

        range_size = (
            upper_boundary
            - lower_boundary
        )

        if range_size <= 0:
            return 0.0

        distance_from_low = (
            price
            - lower_boundary
        )

        distance_from_high = (
            upper_boundary
            - price
        )

        nearest_distance = min(
            distance_from_low,
            distance_from_high,
        )

        return max(
            0.0,
            min(
                nearest_distance
                / range_size,
                0.5,
            ),
        )

    # =========================================================================
    # LOCAL DISPERSION
    # =========================================================================

    def _calculate_local_dispersion(
        self,
        target: SwingPoint,
        swings: list[SwingPoint],
    ) -> float:
        """
        Measure price deviation of nearby internal swings.
        """

        nearby = [
            swing
            for swing in swings
            if abs(
                swing.price
                - target.price
            ) <= LIQUIDITY_TOLERANCE
        ]

        if len(nearby) <= 1:
            return 0.0

        average_price = (
            sum(
                swing.price
                for swing in nearby
            )
            / len(nearby)
        )

        dispersion = sum(
            abs(
                swing.price
                - average_price
            )
            for swing in nearby
        ) / len(nearby)

        return round(
            dispersion,
            10,
        )

    # =========================================================================
    # STRENGTH
    # =========================================================================

    def _calculate_strength(
        self,
        swing_type: SwingType,
        touches: int,
        distance: float,
        dispersion: float,
    ) -> float:
        """
        Calculate structural strength.

        Internal liquidity is intentionally weaker than confirmed external
        liquidity unless repeated internal interaction is present.
        """

        # ---------------------------------------------------------------------
        # Base structural value.
        # ---------------------------------------------------------------------

        strength = 35.0

        # ---------------------------------------------------------------------
        # Touch contribution.
        # ---------------------------------------------------------------------

        strength += min(
            touches * 12.0,
            36.0,
        )

        # ---------------------------------------------------------------------
        # Centrality contribution.
        #
        # Internal levels deeper inside the range are more representative
        # of internal liquidity than levels immediately adjacent to an
        # external boundary.
        # ---------------------------------------------------------------------

        centrality_bonus = min(
            distance * 30.0,
            15.0,
        )

        strength += centrality_bonus

        # ---------------------------------------------------------------------
        # Alignment bonus.
        # ---------------------------------------------------------------------

        if dispersion == 0:

            strength += 8.0

        elif (
            LIQUIDITY_TOLERANCE > 0
            and dispersion
            <= LIQUIDITY_TOLERANCE
        ):

            strength += 4.0

        # ---------------------------------------------------------------------
        # Swing type contributes a small structural distinction.
        # ---------------------------------------------------------------------

        if swing_type in (
            SwingType.HIGH,
            SwingType.LOW,
        ):

            strength += 3.0

        return round(
            min(
                strength,
                100.0,
            ),
            2,
        )

    # =========================================================================
    # CONFIDENCE
    # =========================================================================

    def _calculate_confidence(
        self,
        touches: int,
        distance: float,
        dispersion: float,
        age: int,
    ) -> float:
        """
        Calculate detection confidence.
        """

        confidence = 45.0

        # ---------------------------------------------------------------------
        # Repeated interaction.
        # ---------------------------------------------------------------------

        confidence += min(
            touches * 10.0,
            30.0,
        )

        # ---------------------------------------------------------------------
        # Central position.
        # ---------------------------------------------------------------------

        confidence += min(
            distance * 20.0,
            10.0,
        )

        # ---------------------------------------------------------------------
        # Alignment.
        # ---------------------------------------------------------------------

        if dispersion == 0:

            confidence += 8.0

        elif (
            LIQUIDITY_TOLERANCE > 0
            and dispersion
            <= LIQUIDITY_TOLERANCE
        ):

            confidence += 4.0

        # ---------------------------------------------------------------------
        # Very old levels receive a small freshness penalty.
        # ---------------------------------------------------------------------

        if MAX_AGE > 0:

            age_ratio = min(
                age / MAX_AGE,
                1.0,
            )

            confidence -= (
                age_ratio
                * 8.0
            )

        return round(
            max(
                0.0,
                min(
                    confidence,
                    100.0,
                ),
            ),
            2,
        )

    # =========================================================================
    # EVIDENCE
    # =========================================================================

    def _build_evidence(
        self,
        swing: SwingPoint,
        touches: int,
        distance: float,
        dispersion: float,
        age: int,
    ) -> list[str]:
        """
        Generate explainable evidence for the internal level.
        """

        evidence = [
            (
                "Internal swing detected at "
                f"{swing.price}"
            ),
            (
                f"Swing type: "
                f"{swing.swing_type.value}"
            ),
            (
                f"Structural touches: "
                f"{touches}"
            ),
            (
                f"Normalized boundary distance: "
                f"{distance:.4f}"
            ),
            (
                f"Local dispersion: "
                f"{dispersion}"
            ),
            (
                f"Structural age: "
                f"{age}"
            ),
        ]

        if touches >= 2:

            evidence.append(
                "Repeated internal interaction detected"
            )

        if distance >= 0.25:

            evidence.append(
                "Liquidity located deep inside structural range"
            )

        if dispersion == 0:

            evidence.append(
                "Perfect internal price alignment"
            )

        return evidence

    # =========================================================================
    # DEDUPLICATION
    # =========================================================================

    def _deduplicate(
        self,
        liquidity: list[LiquidityObject],
    ) -> list[LiquidityObject]:
        """
        Remove duplicate internal levels.
        """

        if len(liquidity) <= 1:
            return liquidity

        unique: list[LiquidityObject] = []

        for level in liquidity:

            duplicate = False

            for index, existing in enumerate(
                unique
            ):

                if abs(
                    level.price
                    - existing.price
                ) <= LIQUIDITY_TOLERANCE:

                    duplicate = True

                    # ---------------------------------------------------------
                    # Keep the stronger level.
                    # ---------------------------------------------------------

                    if (
                        level.confidence
                        > existing.confidence
                    ):

                        unique[index] = level

                    break

            if not duplicate:

                unique.append(
                    level
                )

        return unique
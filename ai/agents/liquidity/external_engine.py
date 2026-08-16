"""
===============================================================================
COSMOS External Liquidity Engine

Advanced Institutional External Liquidity Detection.

Responsibilities:
    • Detect major external swing highs
    • Detect major external swing lows
    • Identify structural extremes
    • Calculate liquidity strength
    • Calculate detection confidence
    • Calculate structural age
    • Measure structural range position
    • Generate explainable evidence
    • Handle repeated external levels
    • Prevent duplicate levels
    • Preserve deterministic output
    • Rank major external liquidity

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


class ExternalLiquidityEngine:
    """
    Advanced External Liquidity Engine.

    External liquidity represents major structural liquidity
    positioned at significant market extremes.

    Detection pipeline:

        Swing Structure
            ↓
        Structural Extremes
            ↓
        External High / Low Detection
            ↓
        Repeated-Level Analysis
            ↓
        Strength Calculation
            ↓
        Confidence Calculation
            ↓
        Age Analysis
            ↓
        Evidence Generation
            ↓
        LiquidityObject
    """

    ENGINE_NAME = "external"

    ENGINE_VERSION = "2.0.0"

    LIQUIDITY_SOURCE = "structural_extreme"

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> list[LiquidityObject]:
        """
        Detect major external liquidity.

        Parameters
        ----------
        swings:
            Structural swing points.

        Returns
        -------
        list[LiquidityObject]
            External liquidity levels.
        """

        if not swings:
            return []

        # ---------------------------------------------------------------------
        # Normalize chronological ordering.
        # ---------------------------------------------------------------------

        ordered_swings = sorted(
            swings,
            key=lambda swing: swing.index,
        )

        if len(ordered_swings) < 2:
            return []

        latest_index = max(
            swing.index
            for swing in ordered_swings
        )

        # ---------------------------------------------------------------------
        # Separate highs and lows.
        # ---------------------------------------------------------------------

        highs = [
            swing
            for swing in ordered_swings
            if swing.swing_type == SwingType.HIGH
        ]

        lows = [
            swing
            for swing in ordered_swings
            if swing.swing_type == SwingType.LOW
        ]

        liquidity: list[LiquidityObject] = []

        # ---------------------------------------------------------------------
        # External high.
        # ---------------------------------------------------------------------

        if highs:

            highest = max(
                highs,
                key=lambda swing: (
                    swing.price,
                    swing.index,
                ),
            )

            high_level = self._create_external_level(
                extreme=highest,
                candidates=highs,
                latest_index=latest_index,
                side="high",
            )

            liquidity.append(
                high_level
            )

        # ---------------------------------------------------------------------
        # External low.
        # ---------------------------------------------------------------------

        if lows:

            lowest = min(
                lows,
                key=lambda swing: (
                    swing.price,
                    swing.index,
                ),
            )

            low_level = self._create_external_level(
                extreme=lowest,
                candidates=lows,
                latest_index=latest_index,
                side="low",
            )

            liquidity.append(
                low_level
            )

        # ---------------------------------------------------------------------
        # Safety deduplication.
        # ---------------------------------------------------------------------

        liquidity = self._deduplicate(
            liquidity
        )

        # ---------------------------------------------------------------------
        # Highest significance first.
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
    # LEVEL CREATION
    # =========================================================================

    def _create_external_level(
        self,
        extreme: SwingPoint,
        candidates: list[SwingPoint],
        latest_index: int,
        side: str,
    ) -> LiquidityObject:
        """
        Create one external liquidity object.
        """

        # ---------------------------------------------------------------------
        # Count repeated touches around the structural extreme.
        # ---------------------------------------------------------------------

        touches = self._count_nearby_touches(
            extreme,
            candidates,
        )

        touches = min(
            max(
                touches,
                1,
            ),
            MAX_TOUCHES,
        )

        # ---------------------------------------------------------------------
        # Find all structurally aligned points.
        # ---------------------------------------------------------------------

        aligned = self._aligned_points(
            extreme,
            candidates,
        )

        dispersion = self._calculate_dispersion(
            extreme.price,
            aligned,
        )

        # ---------------------------------------------------------------------
        # Age.
        # ---------------------------------------------------------------------

        age = max(
            latest_index
            - extreme.index,
            0,
        )

        age = min(
            age,
            MAX_AGE,
        )

        # ---------------------------------------------------------------------
        # Structural strength.
        # ---------------------------------------------------------------------

        strength = self._calculate_strength(
            touches=touches,
            dispersion=dispersion,
            age=age,
        )

        # ---------------------------------------------------------------------
        # Detection confidence.
        # ---------------------------------------------------------------------

        confidence = self._calculate_confidence(
            touches=touches,
            dispersion=dispersion,
            age=age,
        )

        # ---------------------------------------------------------------------
        # Evidence.
        # ---------------------------------------------------------------------

        evidence = self._build_evidence(
            extreme=extreme,
            touches=touches,
            dispersion=dispersion,
            age=age,
            side=side,
        )

        return LiquidityObject(
            liquidity_type=LiquidityType.EXTERNAL,

            status=LiquidityStatus.UNTOUCHED,

            price=round(
                extreme.price,
                10,
            ),

            touches=touches,

            strength=strength,

            confidence=confidence,

            quality=0.0,

            age=age,

            distance=0.0,

            source=self.LIQUIDITY_SOURCE,

            evidence=evidence,
        )

    # =========================================================================
    # TOUCH COUNT
    # =========================================================================

    def _count_nearby_touches(
        self,
        extreme: SwingPoint,
        candidates: list[SwingPoint],
    ) -> int:
        """
        Count swing points located around the external extreme.
        """

        return sum(
            1
            for swing in candidates
            if abs(
                swing.price
                - extreme.price
            ) <= LIQUIDITY_TOLERANCE
        )

    # =========================================================================
    # ALIGNED POINTS
    # =========================================================================

    def _aligned_points(
        self,
        extreme: SwingPoint,
        candidates: list[SwingPoint],
    ) -> list[SwingPoint]:
        """
        Return swing points aligned with the external extreme.
        """

        return [
            swing
            for swing in candidates
            if abs(
                swing.price
                - extreme.price
            ) <= LIQUIDITY_TOLERANCE
        ]

    # =========================================================================
    # DISPERSION
    # =========================================================================

    def _calculate_dispersion(
        self,
        extreme_price: float,
        aligned: list[SwingPoint],
    ) -> float:
        """
        Calculate price dispersion around the extreme.
        """

        if len(aligned) <= 1:
            return 0.0

        dispersion = sum(
            abs(
                swing.price
                - extreme_price
            )
            for swing in aligned
        ) / len(aligned)

        return round(
            dispersion,
            10,
        )

    # =========================================================================
    # STRENGTH
    # =========================================================================

    def _calculate_strength(
        self,
        touches: int,
        dispersion: float,
        age: int,
    ) -> float:
        """
        Calculate external structural strength.

        External liquidity starts with a high structural
        base because it represents a major market extreme.
        """

        strength = 75.0

        # ---------------------------------------------------------------------
        # Repeated external interaction.
        # ---------------------------------------------------------------------

        strength += min(
            touches * 6.0,
            18.0,
        )

        # ---------------------------------------------------------------------
        # Price alignment.
        # ---------------------------------------------------------------------

        if dispersion == 0:

            strength += 5.0

        elif (
            LIQUIDITY_TOLERANCE > 0
            and dispersion
            <= LIQUIDITY_TOLERANCE
        ):

            strength += 3.0

        # ---------------------------------------------------------------------
        # Age provides historical significance.
        #
        # Older structural extremes can remain important, but extremely
        # old levels receive a small freshness adjustment.
        # ---------------------------------------------------------------------

        if MAX_AGE > 0:

            age_ratio = min(
                age / MAX_AGE,
                1.0,
            )

            strength += (
                age_ratio
                * 2.0
            )

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
        dispersion: float,
        age: int,
    ) -> float:
        """
        Calculate external liquidity confidence.
        """

        confidence = 78.0

        # ---------------------------------------------------------------------
        # Multiple confirmations.
        # ---------------------------------------------------------------------

        confidence += min(
            touches * 5.0,
            15.0,
        )

        # ---------------------------------------------------------------------
        # Exact alignment.
        # ---------------------------------------------------------------------

        if dispersion == 0:

            confidence += 5.0

        elif (
            LIQUIDITY_TOLERANCE > 0
            and dispersion
            <= LIQUIDITY_TOLERANCE
        ):

            confidence += 3.0

        # ---------------------------------------------------------------------
        # Historical age penalty is intentionally small.
        # ---------------------------------------------------------------------

        if MAX_AGE > 0:

            age_ratio = min(
                age / MAX_AGE,
                1.0,
            )

            confidence -= (
                age_ratio
                * 5.0
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
        extreme: SwingPoint,
        touches: int,
        dispersion: float,
        age: int,
        side: str,
    ) -> list[str]:
        """
        Generate explainable evidence.
        """

        evidence = [
            (
                f"Major external {side} "
                f"detected at {extreme.price}"
            ),
            (
                f"Swing index: "
                f"{extreme.index}"
            ),
            (
                f"Structural touches: "
                f"{touches}"
            ),
            (
                f"Price dispersion: "
                f"{dispersion}"
            ),
            (
                f"Structural age: "
                f"{age}"
            ),
        ]

        if side == "high":

            evidence.append(
                "External buy-side liquidity candidate"
            )

        else:

            evidence.append(
                "External sell-side liquidity candidate"
            )

        if touches >= 2:

            evidence.append(
                "Repeated structural extreme confirmed"
            )

        if dispersion == 0:

            evidence.append(
                "Perfect external price alignment"
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
        Remove duplicate external levels.
        """

        if len(liquidity) <= 1:
            return liquidity

        unique: list[LiquidityObject] = []

        for level in liquidity:

            duplicate = False

            for index, existing in enumerate(
                unique
            ):

                if (
                    level.liquidity_type
                    == existing.liquidity_type
                    and
                    abs(
                        level.price
                        - existing.price
                    )
                    <= LIQUIDITY_TOLERANCE
                ):

                    duplicate = True

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
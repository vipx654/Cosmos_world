"""
===============================================================================
COSMOS Liquidity Quality Engine

Advanced Institutional Liquidity Quality Scoring Engine.

Responsibilities:
    • Evaluate liquidity quality
    • Score structural evidence
    • Score repeated liquidity touches
    • Evaluate liquidity strength
    • Evaluate detection confidence
    • Apply age decay
    • Evaluate price distance
    • Evaluate liquidity status
    • Evaluate liquidity source
    • Reward supporting evidence
    • Detect institutional-quality liquidity
    • Produce explainable quality scores
    • Preserve backward compatibility with LiquidityObject

Quality Score:

    Touches
        +
    Strength
        +
    Confidence
        +
    Age
        +
    Distance
        +
    Status
        +
    Source
        +
    Evidence
        +
    Liquidity Type
        ↓
    Institutional Quality Score

Author: COSMOS Development Team
License: MIT
Version: 2.0.0
===============================================================================
"""

from __future__ import annotations

from ai.agents.liquidity.constants import (
    MAX_AGE,
    MAX_TOUCHES,
)

from ai.agents.liquidity.models import (
    LiquidityObject,
    LiquidityStatus,
    LiquidityType,
)


# =============================================================================
# QUALITY ENGINE
# =============================================================================


class QualityEngine:
    """
    Advanced institutional liquidity quality engine.

    The engine evaluates every liquidity object independently.

    Important:

        The existing public API is preserved:

            QualityEngine().analyze(liquidity)

        and returns:

            list[LiquidityObject]

        The calculated score is stored in:

            level.quality
    """

    ENGINE_NAME = "quality"

    ENGINE_VERSION = "2.0.0"

    # =========================================================================
    # SCORE WEIGHTS
    # =========================================================================

    TOUCH_WEIGHT = 20.0

    STRENGTH_WEIGHT = 20.0

    CONFIDENCE_WEIGHT = 20.0

    AGE_WEIGHT = 10.0

    DISTANCE_WEIGHT = 10.0

    STATUS_WEIGHT = 5.0

    SOURCE_WEIGHT = 5.0

    EVIDENCE_WEIGHT = 5.0

    TYPE_WEIGHT = 5.0

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        liquidity: list[LiquidityObject],
    ) -> list[LiquidityObject]:
        """
        Calculate institutional quality for every liquidity level.

        The method mutates each LiquidityObject in-place and returns the
        original list for complete backward compatibility.
        """

        if not liquidity:
            return liquidity

        for level in liquidity:

            if level is None:
                continue

            score = self._calculate_quality(
                level
            )

            level.quality = round(
                max(
                    0.0,
                    min(
                        score,
                        100.0,
                    ),
                ),
                2,
            )

            self._update_evidence(
                level
            )

        return liquidity

    # =========================================================================
    # MASTER SCORE
    # =========================================================================

    def _calculate_quality(
        self,
        level: LiquidityObject,
    ) -> float:
        """
        Calculate the complete institutional quality score.
        """

        score = 0.0

        # ---------------------------------------------------------------------
        # Touches
        # ---------------------------------------------------------------------

        score += (
            self._touch_score(level)
            * self.TOUCH_WEIGHT
            / 100.0
        )

        # ---------------------------------------------------------------------
        # Strength
        # ---------------------------------------------------------------------

        score += (
            self._strength_score(level)
            * self.STRENGTH_WEIGHT
            / 100.0
        )

        # ---------------------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------------------

        score += (
            self._confidence_score(level)
            * self.CONFIDENCE_WEIGHT
            / 100.0
        )

        # ---------------------------------------------------------------------
        # Age
        # ---------------------------------------------------------------------

        score += (
            self._age_score(level)
            * self.AGE_WEIGHT
            / 100.0
        )

        # ---------------------------------------------------------------------
        # Distance
        # ---------------------------------------------------------------------

        score += (
            self._distance_score(level)
            * self.DISTANCE_WEIGHT
            / 100.0
        )

        # ---------------------------------------------------------------------
        # Status
        # ---------------------------------------------------------------------

        score += (
            self._status_score(level)
            * self.STATUS_WEIGHT
            / 100.0
        )

        # ---------------------------------------------------------------------
        # Source
        # ---------------------------------------------------------------------

        score += (
            self._source_score(level)
            * self.SOURCE_WEIGHT
            / 100.0
        )

        # ---------------------------------------------------------------------
        # Evidence
        # ---------------------------------------------------------------------

        score += (
            self._evidence_score(level)
            * self.EVIDENCE_WEIGHT
            / 100.0
        )

        # ---------------------------------------------------------------------
        # Liquidity Type
        # ---------------------------------------------------------------------

        score += (
            self._type_score(level)
            * self.TYPE_WEIGHT
            / 100.0
        )

        return score

    # =========================================================================
    # TOUCH SCORE
    # =========================================================================

    def _touch_score(
        self,
        level: LiquidityObject,
    ) -> float:
        """
        Score repeated interaction with a liquidity level.

        More touches generally indicate stronger visible liquidity.

        Normalization:

            1 touch  → low
            2 touches → meaningful
            3+ touches → strong
            MAX_TOUCHES → maximum
        """

        touches = max(
            int(level.touches),
            0,
        )

        if touches <= 0:
            return 0.0

        if MAX_TOUCHES <= 0:
            return 0.0

        normalized = (
            touches
            / MAX_TOUCHES
        )

        return min(
            normalized * 100.0,
            100.0,
        )

    # =========================================================================
    # STRENGTH SCORE
    # =========================================================================

    def _strength_score(
        self,
        level: LiquidityObject,
    ) -> float:
        """
        Normalize liquidity strength.
        """

        return self._bounded(
            level.strength
        )

    # =========================================================================
    # CONFIDENCE SCORE
    # =========================================================================

    def _confidence_score(
        self,
        level: LiquidityObject,
    ) -> float:
        """
        Normalize detection confidence.
        """

        return self._bounded(
            level.confidence
        )

    # =========================================================================
    # AGE SCORE
    # =========================================================================

    def _age_score(
        self,
        level: LiquidityObject,
    ) -> float:
        """
        Calculate age quality.

        Fresh liquidity receives a higher score.

        Older liquidity gradually loses quality, but never becomes
        automatically invalid.
        """

        age = max(
            int(level.age),
            0,
        )

        if MAX_AGE <= 0:
            return 100.0

        if age >= MAX_AGE:
            return 0.0

        freshness = (
            1.0
            - (
                age
                / MAX_AGE
            )
        )

        return self._bounded(
            freshness * 100.0
        )

    # =========================================================================
    # DISTANCE SCORE
    # =========================================================================

    def _distance_score(
        self,
        level: LiquidityObject,
    ) -> float:
        """
        Evaluate distance from current/reference price.

        A zero distance is considered highly relevant.

        Because LiquidityObject does not currently contain the current
        market price, the engine treats the stored distance as the
        normalized distance supplied by upstream analysis.
        """

        try:
            distance = abs(
                float(level.distance)
            )

        except (
            TypeError,
            ValueError,
        ):
            return 50.0

        if distance <= 0.0:
            return 100.0

        # ---------------------------------------------------------------------
        # Smooth decay.
        #
        # This avoids an abrupt quality cliff.
        # ---------------------------------------------------------------------

        score = (
            100.0
            / (
                1.0
                + distance
            )
        )

        return self._bounded(
            score
        )

    # =========================================================================
    # STATUS SCORE
    # =========================================================================

    def _status_score(
        self,
        level: LiquidityObject,
    ) -> float:
        """
        Evaluate liquidity status.
        """

        status = level.status

        if status == LiquidityStatus.UNTOUCHED:
            return 100.0

        if status == LiquidityStatus.PARTIAL:
            return 65.0

        if status == LiquidityStatus.SWEPT:
            return 25.0

        return 50.0

    # =========================================================================
    # SOURCE SCORE
    # =========================================================================

    def _source_score(
        self,
        level: LiquidityObject,
    ) -> float:
        """
        Evaluate the quality of the detection source.
        """

        source = (
            str(
                level.source
            )
            .strip()
            .lower()
        )

        if not source:
            return 50.0

        # ---------------------------------------------------------------------
        # High-quality structural sources.
        # ---------------------------------------------------------------------

        high_quality_sources = (
            "equal_highs",
            "equal_lows",
            "swing",
            "market_structure",
            "smc",
            "order_block",
            "liquidity",
            "external",
        )

        for item in high_quality_sources:

            if item in source:
                return 100.0

        # ---------------------------------------------------------------------
        # Generic but valid source.
        # ---------------------------------------------------------------------

        return 70.0

    # =========================================================================
    # EVIDENCE SCORE
    # =========================================================================

    def _evidence_score(
        self,
        level: LiquidityObject,
    ) -> float:
        """
        Evaluate the amount of supporting evidence.
        """

        if not level.evidence:
            return 35.0

        evidence_count = len(
            level.evidence
        )

        # ---------------------------------------------------------------------
        # Evidence saturation.
        # ---------------------------------------------------------------------

        score = min(
            evidence_count * 20.0,
            100.0,
        )

        return score

    # =========================================================================
    # LIQUIDITY TYPE SCORE
    # =========================================================================

    def _type_score(
        self,
        level: LiquidityObject,
    ) -> float:
        """
        Apply structural importance according to liquidity type.
        """

        liquidity_type = (
            level.liquidity_type
        )

        if liquidity_type == LiquidityType.EXTERNAL:
            return 100.0

        if liquidity_type == LiquidityType.BUY_SIDE:
            return 95.0

        if liquidity_type == LiquidityType.SELL_SIDE:
            return 95.0

        if liquidity_type == LiquidityType.INTERNAL:
            return 75.0

        return 60.0

    # =========================================================================
    # EVIDENCE ENRICHMENT
    # =========================================================================

    def _update_evidence(
        self,
        level: LiquidityObject,
    ) -> None:
        """
        Add an explainable quality assessment to the existing evidence list.

        No new model fields are required.
        """

        evidence = list(
            level.evidence
        )

        evidence.append(
            (
                f"Quality score: "
                f"{level.quality:.2f}"
            )
        )

        # ---------------------------------------------------------------------
        # Quality classification.
        # ---------------------------------------------------------------------

        if level.quality >= 85.0:

            evidence.append(
                "Institutional quality: VERY_HIGH"
            )

        elif level.quality >= 70.0:

            evidence.append(
                "Institutional quality: HIGH"
            )

        elif level.quality >= 50.0:

            evidence.append(
                "Institutional quality: MODERATE"
            )

        elif level.quality >= 30.0:

            evidence.append(
                "Institutional quality: LOW"
            )

        else:

            evidence.append(
                "Institutional quality: VERY_LOW"
            )

        level.evidence = (
            self._unique_evidence(
                evidence
            )
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def _bounded(
        value: float,
    ) -> float:
        """
        Clamp a numeric value between 0 and 100.
        """

        try:

            value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

        if value != value:
            return 0.0

        if value == float("inf"):
            return 100.0

        if value == float("-inf"):
            return 0.0

        return max(
            0.0,
            min(
                value,
                100.0,
            ),
        )

    # =========================================================================
    # DEDUPLICATION
    # =========================================================================

    @staticmethod
    def _unique_evidence(
        evidence: list[str],
    ) -> list[str]:
        """
        Remove duplicate evidence while preserving order.
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
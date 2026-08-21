"""
===============================================================================
COSMOS Fair Value Gap Probability Engine V2

Calculates a normalized heuristic probability score for detected Fair Value
Gaps.

IMPORTANT:

    This value is NOT a statistically validated win probability.

It represents COSMOS's current structural assessment of the FVG based on
available evidence.

Future calibration can replace or augment this heuristic with:

    - Backtest statistics
    - Symbol-specific calibration
    - Timeframe-specific calibration
    - Session statistics
    - Historical FVG outcomes
    - Machine-learning probability calibration

Pipeline:

    Detection
        ↓
    Mitigation
        ↓
    Inversion
        ↓
    Probability
        ↓
    Confidence
        ↓
    Confirmation

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.constants import (
    CONFIRMED_INVERSION_PENALTY,
    DEFAULT_PROBABILITY,
    FULL_FILL_PENALTY,
    INVALIDATION_PENALTY,
    LOW_QUALITY,
    MAX_PROBABILITY,
    MIN_PROBABILITY,
    MODERATE_QUALITY,
    PROBABILITY_BASE_WEIGHT,
    PROBABILITY_CONFLUENCE_WEIGHT,
    PROBABILITY_DISPLACEMENT_WEIGHT,
    PROBABILITY_FRESHNESS_WEIGHT,
    PROBABILITY_QUALITY_WEIGHT,
    PROBABILITY_STRENGTH_WEIGHT,
    POTENTIAL_INVERSION_PENALTY,
    VERY_HIGH_QUALITY,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGDirection,
    FVGStatus,
    InversionStatus,
    MitigationStatus,
)


class ProbabilityEngine:
    """
    Calculates the heuristic probability score of each FVG.

    The engine is intentionally deterministic.

    Current inputs:

        - Existing probability
        - FVG confidence
        - FVG strength
        - Structural quality
        - Evidence quality
        - Freshness / lifecycle
        - Mitigation
        - Inversion
        - Active direction

    Reserved architecture:

        - Trend
        - Market structure
        - Liquidity
        - Sweep
        - Order Block
        - SMC
        - Volume
        - Session
        - HTF
        - Displacement
        - Historical calibration

    These can be injected later without changing the public API.
    """

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        fvgs: list[FairValueGap],
    ) -> list[FairValueGap]:
        """
        Calculate probability for every supplied FVG.

        The original list is mutated in place and returned for compatibility
        with the existing FVG pipeline.
        """

        if not fvgs:
            return []

        for fvg in fvgs:
            self._calculate_probability(fvg)

        return fvgs

    # =========================================================================
    # CORE CALCULATION
    # =========================================================================

    def _calculate_probability(
        self,
        fvg: FairValueGap,
    ) -> None:
        """
        Calculate and apply the probability score for one FVG.
        """

        # ---------------------------------------------------------------------
        # Normalize primitive inputs.
        # ---------------------------------------------------------------------

        existing_probability = self._clamp(
            fvg.probability
        )

        confidence = self._clamp(
            fvg.confidence
        )

        strength = self._clamp(
            fvg.strength
        )

        quality = self._quality_score(
            fvg
        )

        freshness = self._freshness_score(
            fvg
        )

        confluence = self._confluence_score(
            fvg
        )

        displacement = self._displacement_score(
            fvg
        )

        # ---------------------------------------------------------------------
        # Weighted score.
        #
        # The base contribution keeps the result anchored around the
        # existing/default probability.
        # ---------------------------------------------------------------------

        score = (
            existing_probability
            * PROBABILITY_BASE_WEIGHT
        )

        score += (
            strength
            * PROBABILITY_STRENGTH_WEIGHT
        )

        score += (
            quality
            * PROBABILITY_QUALITY_WEIGHT
        )

        score += (
            confluence
            * PROBABILITY_CONFLUENCE_WEIGHT
        )

        score += (
            freshness
            * PROBABILITY_FRESHNESS_WEIGHT
        )

        score += (
            displacement
            * PROBABILITY_DISPLACEMENT_WEIGHT
        )

        # ---------------------------------------------------------------------
        # Lifecycle adjustments.
        # ---------------------------------------------------------------------

        score += self._mitigation_adjustment(
            fvg
        )

        # ---------------------------------------------------------------------
        # Inversion adjustment.
        # ---------------------------------------------------------------------

        score += self._inversion_adjustment(
            fvg
        )

        # ---------------------------------------------------------------------
        # Direction validity.
        # ---------------------------------------------------------------------

        score += self._direction_adjustment(
            fvg
        )

        # ---------------------------------------------------------------------
        # Final normalization.
        # ---------------------------------------------------------------------

        score = self._clamp(
            score
        )

        fvg.probability = round(
            score,
            2,
        )

        # ---------------------------------------------------------------------
        # Add deterministic probability classification.
        # ---------------------------------------------------------------------

        self._add_probability_evidence(
            fvg
        )

    # =========================================================================
    # QUALITY
    # =========================================================================

    @staticmethod
    def _quality_score(
        fvg: FairValueGap,
    ) -> float:
        """
        Estimate structural FVG quality from available evidence.

        This is deliberately conservative because the dedicated confluence
        engines have not yet been integrated into the FVG probability layer.
        """

        score = 50.0

        confidence = ProbabilityEngine._clamp(
            fvg.confidence
        )

        strength = ProbabilityEngine._clamp(
            fvg.strength
        )

        # Confidence and strength are already meaningful structural signals.
        score += (
            confidence - 50.0
        ) * 0.25

        score += (
            strength - 50.0
        ) * 0.25

        evidence_count = len(
            fvg.evidence
        )

        if evidence_count >= 5:
            score += 15.0

        elif evidence_count >= 4:
            score += 10.0

        elif evidence_count >= 2:
            score += 5.0

        # Strong confidence/strength combination.
        if (
            confidence >= VERY_HIGH_QUALITY
            and
            strength >= VERY_HIGH_QUALITY
        ):
            score += 10.0

        elif (
            confidence >= MODERATE_QUALITY
            and
            strength >= MODERATE_QUALITY
        ):
            score += 5.0

        elif (
            confidence < LOW_QUALITY
            or
            strength < LOW_QUALITY
        ):
            score -= 5.0

        return ProbabilityEngine._clamp(
            score
        )

    # =========================================================================
    # FRESHNESS
    # =========================================================================

    @staticmethod
    def _freshness_score(
        fvg: FairValueGap,
    ) -> float:
        """
        Convert lifecycle state into a normalized freshness score.
        """

        if fvg.status == FVGStatus.FRESH:
            return 100.0

        if fvg.status == FVGStatus.TESTED:
            return 80.0

        if fvg.status == FVGStatus.PARTIAL:
            return 60.0

        if fvg.status == FVGStatus.FILLED:
            return 20.0

        if fvg.status == FVGStatus.INVALID:
            return 0.0

        return 50.0

    # =========================================================================
    # CONFLUENCE
    # =========================================================================

    @staticmethod
    def _confluence_score(
        fvg: FairValueGap,
    ) -> float:
        """
        Estimate currently available confluence.

        Dedicated COSMOS engines can later populate explicit confluence data.
        Until then, evidence is used as a conservative proxy.
        """

        evidence_count = len(
            fvg.evidence
        )

        if evidence_count >= 5:
            return 90.0

        if evidence_count >= 4:
            return 80.0

        if evidence_count >= 3:
            return 70.0

        if evidence_count >= 2:
            return 60.0

        if evidence_count >= 1:
            return 50.0

        return 40.0

    # =========================================================================
    # DISPLACEMENT
    # =========================================================================

    @staticmethod
    def _displacement_score(
        fvg: FairValueGap,
    ) -> float:
        """
        Estimate displacement quality from FVG strength and evidence.

        This remains a proxy until the dedicated displacement/volume engines
        are connected to the FVG context.
        """

        score = ProbabilityEngine._clamp(
            fvg.strength
        )

        evidence_text = " ".join(
            str(item).lower()
            for item in fvg.evidence
        )

        if (
            "displacement"
            in evidence_text
        ):
            score += 15.0

        if (
            "significant gap"
            in evidence_text
        ):
            score += 10.0

        return ProbabilityEngine._clamp(
            score
        )

    # =========================================================================
    # MITIGATION
    # =========================================================================

    @staticmethod
    def _mitigation_adjustment(
        fvg: FairValueGap,
    ) -> float:
        """
        Apply lifecycle/mitigation adjustments.
        """

        if (
            fvg.mitigation_status
            == MitigationStatus.UNTOUCHED
        ):
            return 5.0

        if (
            fvg.mitigation_status
            == MitigationStatus.PARTIAL
        ):
            return -3.0

        if (
            fvg.mitigation_status
            == MitigationStatus.FULL
        ):
            return -FULL_FILL_PENALTY

        if (
            fvg.mitigation_status
            == MitigationStatus.INVALIDATED
        ):
            return -INVALIDATION_PENALTY

        return 0.0

    # =========================================================================
    # INVERSION
    # =========================================================================

    @staticmethod
    def _inversion_adjustment(
        fvg: FairValueGap,
    ) -> float:
        """
        Apply inversion adjustments.

        A confirmed IFVG receives a penalty because the original thesis has
        failed, but it remains usable because the active direction has been
        reversed by the inversion engine.
        """

        if (
            fvg.inversion_status
            == InversionStatus.CONFIRMED
            or
            fvg.inverted
        ):
            return -CONFIRMED_INVERSION_PENALTY

        if (
            fvg.inversion_status
            == InversionStatus.POTENTIAL
        ):
            return -POTENTIAL_INVERSION_PENALTY

        return 0.0

    # =========================================================================
    # DIRECTION
    # =========================================================================

    @staticmethod
    def _direction_adjustment(
        fvg: FairValueGap,
    ) -> float:
        """
        Reward a valid active directional thesis.
        """

        if fvg.direction in (
            FVGDirection.BULLISH,
            FVGDirection.BEARISH,
        ):
            return 5.0

        return -10.0

    # =========================================================================
    # EVIDENCE
    # =========================================================================

    @staticmethod
    def _add_probability_evidence(
        fvg: FairValueGap,
    ) -> None:
        """
        Add exactly one probability classification label.
        """

        labels = {
            "High FVG Probability",
            "Moderate FVG Probability",
            "Low FVG Probability",
        }

        # Remove stale classification labels first.
        fvg.evidence[:] = [
            evidence
            for evidence in fvg.evidence
            if evidence not in labels
        ]

        probability = (
            fvg.probability
        )

        if probability >= 80.0:
            label = (
                "High FVG Probability"
            )

        elif probability >= 65.0:
            label = (
                "Moderate FVG Probability"
            )

        else:
            label = (
                "Low FVG Probability"
            )

        fvg.evidence.append(
            label
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        """
        Clamp a score to the configured probability range.
        """

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            value = (
                DEFAULT_PROBABILITY
            )

        return max(
            MIN_PROBABILITY,
            min(
                MAX_PROBABILITY,
                value,
            ),
        )
"""
===============================================================================
COSMOS Fair Value Gap Confidence Engine V3

Produces the final confidence score for each Fair Value Gap.

Responsibilities
----------------
- Combine finalized FVG quality signals.
- Incorporate probability, strength and confluence-ready inputs.
- Respect lifecycle / mitigation state.
- Respect validity and inversion state.
- Produce deterministic 0-100 confidence.
- Generate explainable confidence evidence.
- Remain safe to run repeatedly.

Design
------
Confidence is NOT a win-rate prediction.

It is a normalized structural confidence score describing how strongly
COSMOS currently supports the FVG as an actionable market structure.

Pipeline position:

    Detection
        ↓
    Mitigation
        ↓
    Inversion
        ↓
    Probability
        ↓
    Confidence  ← this engine
        ↓
    Confirmation
        ↓
    Mapping
        ↓
    Ranking
        ↓
    Final Analysis

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.constants import (
    CONFIDENCE_PROBABILITY_WEIGHT,
    CONFIDENCE_QUALITY_WEIGHT,
    CONFIDENCE_STRENGTH_WEIGHT,
    CONFIDENCE_VALIDITY_WEIGHT,
    CONFIDENCE_CONFLUENCE_WEIGHT,
    DEFAULT_CONFIDENCE,
    MAX_CONFIDENCE,
    MIN_CONFIDENCE,
    PARTIAL_MITIGATION_PENALTY,
    DEEP_MITIGATION_PENALTY,
    FULL_FILL_PENALTY,
    INVALIDATION_PENALTY,
    POTENTIAL_INVERSION_PENALTY,
    CONFIRMED_INVERSION_PENALTY,
    UNTOUCHED_BONUS,
    MIN_EVIDENCE_FOR_BONUS,
    STRONG_EVIDENCE_COUNT,
    MAX_EVIDENCE_BONUS,
    HIGH_QUALITY,
    VERY_HIGH_QUALITY,
    EXTREME_QUALITY,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGStatus,
    InversionStatus,
    MitigationStatus,
)


class ConfidenceEngine:
    """
    Calculates final structural confidence for FVGs.

    Important
    ---------
    This score is NOT a statistically validated probability of winning a
    trade. It represents COSMOS's current structural confidence in the FVG.

    The engine is intentionally:

        deterministic
        bounded
        explainable
        idempotent
        dependency-safe

    Future versions can consume additional confluence signals such as:

        - trend
        - market structure
        - liquidity
        - sweep
        - order block
        - SMC
        - volume
        - session
        - HTF alignment
        - displacement
    """

    _LABELS = {
        "very_high": "Very High FVG Confidence",
        "high": "High FVG Confidence",
        "moderate": "Moderate FVG Confidence",
        "low": "Low FVG Confidence",
    }

    def analyze(
        self,
        fvgs: list[FairValueGap],
    ) -> list[FairValueGap]:
        """
        Calculate final confidence for every FVG.

        Parameters
        ----------
        fvgs:
            Detected and already processed FVG objects.

        Returns
        -------
        list[FairValueGap]
            The same FVG objects with updated confidence/evidence.
        """

        if not fvgs:
            return []

        for fvg in fvgs:
            self._calculate(fvg)

        return fvgs

    # =========================================================================
    # CORE CALCULATION
    # =========================================================================

    def _calculate(
        self,
        fvg: FairValueGap,
    ) -> None:
        """
        Calculate confidence for one FVG.
        """

        # ---------------------------------------------------------------------
        # Normalize source values.
        # ---------------------------------------------------------------------

        probability = self._bounded(
            fvg.probability,
        )

        strength = self._bounded(
            fvg.strength,
        )

        quality = self._derive_quality(
            fvg,
        )

        validity = (
            MAX_CONFIDENCE
            if fvg.valid
            else MIN_CONFIDENCE
        )

        # ---------------------------------------------------------------------
        # Base weighted confidence.
        #
        # All components are normalized to 0-100.
        # ---------------------------------------------------------------------

        confidence = (
            quality
            * CONFIDENCE_QUALITY_WEIGHT
            +
            probability
            * CONFIDENCE_PROBABILITY_WEIGHT
            +
            strength
            * CONFIDENCE_STRENGTH_WEIGHT
            +
            validity
            * CONFIDENCE_VALIDITY_WEIGHT
        )

        # ---------------------------------------------------------------------
        # Confluence placeholder.
        #
        # Current FVG model does not yet expose a dedicated confluence score.
        # Therefore the existing confidence acts as the neutral confluence
        # input rather than inventing external intelligence.
        # ---------------------------------------------------------------------

        confluence = self._existing_confluence(
            fvg,
        )

        confidence = (
            confidence
            +
            confluence
            * CONFIDENCE_CONFLUENCE_WEIGHT
        )

        # ---------------------------------------------------------------------
        # Lifecycle adjustments.
        # ---------------------------------------------------------------------

        confidence += self._lifecycle_adjustment(
            fvg,
        )

        # ---------------------------------------------------------------------
        # Inversion adjustments.
        # ---------------------------------------------------------------------

        confidence += self._inversion_adjustment(
            fvg,
        )

        # ---------------------------------------------------------------------
        # Evidence quality.
        # ---------------------------------------------------------------------

        confidence += self._evidence_adjustment(
            fvg,
        )

        # ---------------------------------------------------------------------
        # Invalidated FVGs receive a hard safety reduction.
        # ---------------------------------------------------------------------

        if not fvg.valid:
            confidence -= INVALIDATION_PENALTY

        # ---------------------------------------------------------------------
        # Final normalization.
        # ---------------------------------------------------------------------

        confidence = self._bounded(
            confidence,
        )

        fvg.confidence = round(
            confidence,
            2,
        )

        self._update_evidence(
            fvg,
        )

    # =========================================================================
    # NORMALIZATION
    # =========================================================================

    @staticmethod
    def _bounded(
        value: float,
    ) -> float:
        """
        Clamp a numeric score to the configured 0-100 range.

        Invalid numeric input falls back to the neutral confidence level.
        """

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return DEFAULT_CONFIDENCE

        if value != value:  # NaN
            return DEFAULT_CONFIDENCE

        return max(
            MIN_CONFIDENCE,
            min(
                MAX_CONFIDENCE,
                value,
            ),
        )

    # =========================================================================
    # QUALITY
    # =========================================================================

    def _derive_quality(
        self,
        fvg: FairValueGap,
    ) -> float:
        """
        Derive structural quality from the available FVG signals.

        If future models expose an explicit quality_score field, this method
        can consume it directly without changing the orchestration pipeline.
        """

        strength = self._bounded(
            fvg.strength,
        )

        probability = self._bounded(
            fvg.probability,
        )

        existing_confidence = self._bounded(
            fvg.confidence,
        )

        # Weighted structural quality.
        quality = (
            strength * 0.45
            +
            probability * 0.30
            +
            existing_confidence * 0.25
        )

        return self._bounded(
            quality,
        )

    # =========================================================================
    # CONFLUENCE
    # =========================================================================

    def _existing_confluence(
        self,
        fvg: FairValueGap,
    ) -> float:
        """
        Return currently available confluence information.

        The current FairValueGap model does not contain a dedicated
        confluence_score field, so we derive a conservative proxy from
        evidence density.

        This avoids fabricating intelligence that the upstream engines have
        not actually supplied.
        """

        evidence_count = len(
            self._unique_evidence(
                fvg,
            )
        )

        if evidence_count >= STRONG_EVIDENCE_COUNT:
            return 85.0

        if evidence_count >= MIN_EVIDENCE_FOR_BONUS + 2:
            return 70.0

        if evidence_count >= MIN_EVIDENCE_FOR_BONUS:
            return 60.0

        if evidence_count == 1:
            return 50.0

        return 40.0

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    @staticmethod
    def _lifecycle_adjustment(
        fvg: FairValueGap,
    ) -> float:
        """
        Apply lifecycle-specific confidence adjustments.
        """

        status = fvg.status
        mitigation = fvg.mitigation_status

        adjustment = 0.0

        # Fresh untouched FVGs retain the strongest structural premium.
        if (
            status == FVGStatus.FRESH
            and
            mitigation == MitigationStatus.UNTOUCHED
        ):
            adjustment += UNTOUCHED_BONUS

        elif status == FVGStatus.PARTIAL:
            adjustment -= PARTIAL_MITIGATION_PENALTY

            # Deep mitigation is more significant than normal partial
            # mitigation.
            if fvg.fill_ratio >= 0.75:
                adjustment -= DEEP_MITIGATION_PENALTY

        elif status == FVGStatus.TESTED:
            adjustment -= PARTIAL_MITIGATION_PENALTY

        elif status == FVGStatus.FILLED:
            adjustment -= FULL_FILL_PENALTY

        elif status == FVGStatus.INVALID:
            adjustment -= INVALIDATION_PENALTY

        # Explicit mitigation state takes precedence over ambiguous lifecycle
        # labels.
        if mitigation == MitigationStatus.FULL:
            adjustment -= FULL_FILL_PENALTY

        elif mitigation == MitigationStatus.INVALIDATED:
            adjustment -= INVALIDATION_PENALTY

        return adjustment

    # =========================================================================
    # INVERSION
    # =========================================================================

    @staticmethod
    def _inversion_adjustment(
        fvg: FairValueGap,
    ) -> float:
        """
        Apply inversion penalties.

        An IFVG remains potentially useful, but the original directional
        premise has been invalidated.
        """

        if (
            fvg.inversion_status
            == InversionStatus.CONFIRMED
        ):
            return -CONFIRMED_INVERSION_PENALTY

        if (
            fvg.inversion_status
            == InversionStatus.POTENTIAL
        ):
            return -POTENTIAL_INVERSION_PENALTY

        return 0.0

    # =========================================================================
    # EVIDENCE
    # =========================================================================

    def _evidence_adjustment(
        self,
        fvg: FairValueGap,
    ) -> float:
        """
        Reward evidence density without allowing evidence spam to dominate
        the actual structural score.
        """

        evidence_count = len(
            self._unique_evidence(
                fvg,
            )
        )

        if evidence_count >= STRONG_EVIDENCE_COUNT:
            return MAX_EVIDENCE_BONUS

        if evidence_count >= MIN_EVIDENCE_FOR_BONUS + 2:
            return 5.0

        if evidence_count >= MIN_EVIDENCE_FOR_BONUS:
            return 2.0

        return 0.0

    @staticmethod
    def _unique_evidence(
        fvg: FairValueGap,
    ) -> list[str]:
        """
        Return evidence without duplicates while preserving order.
        """

        seen: set[str] = set()
        result: list[str] = []

        for item in fvg.evidence:
            text = str(item).strip()

            if not text:
                continue

            if text in seen:
                continue

            seen.add(text)
            result.append(text)

        return result

    # =========================================================================
    # LABELING
    # =========================================================================

    def _update_evidence(
        self,
        fvg: FairValueGap,
    ) -> None:
        """
        Replace the previous confidence label with the current label.

        This makes the engine idempotent: repeatedly running the engine does
        not create duplicate or contradictory confidence labels.
        """

        labels = set(
            self._LABELS.values()
        )

        fvg.evidence = [
            item
            for item in fvg.evidence
            if item not in labels
        ]

        confidence = fvg.confidence

        if confidence >= EXTREME_QUALITY:
            label = self._LABELS["very_high"]

        elif confidence >= VERY_HIGH_QUALITY:
            label = self._LABELS["very_high"]

        elif confidence >= HIGH_QUALITY:
            label = self._LABELS["high"]

        elif confidence >= 55.0:
            label = self._LABELS["moderate"]

        else:
            label = self._LABELS["low"]

        fvg.evidence.append(
            label
        )
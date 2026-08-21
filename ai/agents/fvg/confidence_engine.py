"""
===============================================================================
COSMOS Fair Value Gap Confidence Engine V4

Produces the final structural confidence score for each Fair Value Gap.

Responsibilities
----------------
- Combine finalized FVG structural signals.
- Incorporate probability and strength.
- Consume optional confluence information when available.
- Respect lifecycle / mitigation state.
- Respect validity and inversion state.
- Produce deterministic bounded 0-100 confidence.
- Generate explainable confidence evidence.
- Remain safe to execute repeatedly.
- Avoid feedback loops from previously calculated confidence.

Design
------
Confidence is NOT a win-rate prediction.

It represents COSMOS's current structural confidence that an FVG remains
actionable based on the information actually supplied by upstream engines.

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
    CONFIDENCE_CONFLUENCE_WEIGHT,
    CONFIDENCE_PROBABILITY_WEIGHT,
    CONFIDENCE_QUALITY_WEIGHT,
    CONFIDENCE_STRENGTH_WEIGHT,
    CONFIDENCE_VALIDITY_WEIGHT,
    DEFAULT_CONFIDENCE,
    EXTREME_QUALITY,
    FULL_FILL_PENALTY,
    HIGH_QUALITY,
    INVALIDATION_PENALTY,
    MAX_CONFIDENCE,
    MAX_EVIDENCE_BONUS,
    MIN_CONFIDENCE,
    MIN_EVIDENCE_FOR_BONUS,
    PARTIAL_MITIGATION_PENALTY,
    POTENTIAL_INVERSION_PENALTY,
    CONFIRMED_INVERSION_PENALTY,
    STRONG_EVIDENCE_COUNT,
    UNTOUCHED_BONUS,
    VERY_HIGH_QUALITY,
    DEEP_MITIGATION_PENALTY,
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
    Confidence is not a statistically validated probability of winning a
    trade.

    It represents COSMOS's current structural confidence in the FVG.

    Properties
    ----------
    deterministic
        Same FVG state produces the same score.

    bounded
        Output is always between 0 and 100.

    explainable
        Confidence labels and evidence are attached to the FVG.

    idempotent
        Running the engine repeatedly does not progressively alter the score
        merely because the previous confidence value was stored on the FVG.

    dependency-safe
        Missing optional confluence information does not break analysis.
    """

    _LABELS = {
        "very_high": "Very High FVG Confidence",
        "high": "High FVG Confidence",
        "moderate": "Moderate FVG Confidence",
        "low": "Low FVG Confidence",
    }

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        fvgs: list[FairValueGap],
    ) -> list[FairValueGap]:
        """
        Calculate confidence for every supplied FVG.

        The same FVG objects are returned after their confidence and evidence
        have been updated.
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
        Calculate confidence for a single FVG.
        """

        # ---------------------------------------------------------------------
        # Normalize upstream signals.
        # ---------------------------------------------------------------------

        probability = self._bounded(
            getattr(
                fvg,
                "probability",
                DEFAULT_CONFIDENCE,
            )
        )

        strength = self._bounded(
            getattr(
                fvg,
                "strength",
                DEFAULT_CONFIDENCE,
            )
        )

        quality = self._derive_quality(
            fvg,
            probability=probability,
            strength=strength,
        )

        validity = (
            MAX_CONFIDENCE
            if bool(
                getattr(
                    fvg,
                    "valid",
                    True,
                )
            )
            else MIN_CONFIDENCE
        )

        confluence = self._existing_confluence(
            fvg,
        )

        # ---------------------------------------------------------------------
        # Weighted base score.
        #
        # The configured weights sum to 1.0:
        #
        # quality      = 30%
        # probability  = 20%
        # strength     = 15%
        # validity     = 10%
        # confluence   = 25%
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
            +
            confluence
            * CONFIDENCE_CONFLUENCE_WEIGHT
        )

        # ---------------------------------------------------------------------
        # Lifecycle.
        # ---------------------------------------------------------------------

        confidence += self._lifecycle_adjustment(
            fvg,
        )

        # ---------------------------------------------------------------------
        # Inversion.
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
        # Hard validity protection.
        # ---------------------------------------------------------------------

        if not bool(
            getattr(
                fvg,
                "valid",
                True,
            )
        ):
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
        Clamp a value to the configured confidence range.

        Invalid numeric values return the neutral score.
        """

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return DEFAULT_CONFIDENCE

        # NaN
        if value != value:
            return DEFAULT_CONFIDENCE

        # Positive / negative infinity.
        if value == float("inf"):
            return MAX_CONFIDENCE

        if value == float("-inf"):
            return MIN_CONFIDENCE

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
        *,
        probability: float,
        strength: float,
    ) -> float:
        """
        Derive structural quality from upstream signals.

        Important:
            Previously calculated confidence is deliberately NOT included.

        This prevents:

            old confidence
                ↓
            quality
                ↓
            new confidence
                ↓
            quality
                ↓
            ...

        from creating a feedback loop when the engine is executed repeatedly.
        """

        evidence_count = len(
            self._unique_evidence(
                fvg,
            )
        )

        # ---------------------------------------------------------------------
        # Core structural quality.
        # ---------------------------------------------------------------------

        quality = (
            strength * 0.55
            +
            probability * 0.45
        )

        # ---------------------------------------------------------------------
        # Evidence quality modifier.
        #
        # Evidence is intentionally capped so evidence spam cannot dominate
        # the structural inputs.
        # ---------------------------------------------------------------------

        if evidence_count >= STRONG_EVIDENCE_COUNT:
            quality += 5.0

        elif evidence_count >= MIN_EVIDENCE_FOR_BONUS:
            quality += 2.0

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
        Return the best currently available confluence score.

        If a future FairValueGap model exposes `confluence_score`, it is
        consumed automatically.

        Otherwise a conservative evidence-density proxy is used.

        No external intelligence is fabricated.
        """

        explicit = getattr(
            fvg,
            "confluence_score",
            None,
        )

        if explicit is not None:
            try:
                return self._bounded(
                    float(explicit)
                )
            except (
                TypeError,
                ValueError,
            ):
                pass

        evidence_count = len(
            self._unique_evidence(
                fvg,
            )
        )

        if evidence_count >= STRONG_EVIDENCE_COUNT:
            return 85.0

        if evidence_count >= (
            MIN_EVIDENCE_FOR_BONUS + 2
        ):
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

        status = getattr(
            fvg,
            "status",
            FVGStatus.FRESH,
        )

        mitigation = getattr(
            fvg,
            "mitigation_status",
            MitigationStatus.UNTOUCHED,
        )

        fill_ratio = 0.0

        try:
            fill_ratio = max(
                0.0,
                min(
                    1.0,
                    float(
                        getattr(
                            fvg,
                            "fill_ratio",
                            0.0,
                        )
                    ),
                ),
            )
        except (
            TypeError,
            ValueError,
        ):
            fill_ratio = 0.0

        adjustment = 0.0

        # ---------------------------------------------------------------------
        # Fresh untouched FVG.
        # ---------------------------------------------------------------------

        if (
            status == FVGStatus.FRESH
            and
            mitigation == MitigationStatus.UNTOUCHED
        ):
            adjustment += UNTOUCHED_BONUS

        # ---------------------------------------------------------------------
        # Partial mitigation.
        # ---------------------------------------------------------------------

        elif status == FVGStatus.PARTIAL:

            adjustment -= (
                PARTIAL_MITIGATION_PENALTY
            )

            if fill_ratio >= 0.75:
                adjustment -= (
                    DEEP_MITIGATION_PENALTY
                )

        # ---------------------------------------------------------------------
        # Tested.
        # ---------------------------------------------------------------------

        elif status == FVGStatus.TESTED:
            adjustment -= (
                PARTIAL_MITIGATION_PENALTY
            )

        # ---------------------------------------------------------------------
        # Filled.
        # ---------------------------------------------------------------------

        elif status == FVGStatus.FILLED:
            adjustment -= (
                FULL_FILL_PENALTY
            )

        # ---------------------------------------------------------------------
        # Invalid.
        # ---------------------------------------------------------------------

        elif status == FVGStatus.INVALID:
            adjustment -= (
                INVALIDATION_PENALTY
            )

        # ---------------------------------------------------------------------
        # Explicit mitigation state has priority.
        # ---------------------------------------------------------------------

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

        An inverted FVG may remain useful as an IFVG, but the original
        directional thesis has been invalidated.
        """

        inversion_status = getattr(
            fvg,
            "inversion_status",
            InversionStatus.NONE,
        )

        if (
            inversion_status
            == InversionStatus.CONFIRMED
        ):
            return -CONFIRMED_INVERSION_PENALTY

        if (
            inversion_status
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
        Reward meaningful evidence density.

        Evidence contribution is capped.
        """

        evidence_count = len(
            self._unique_evidence(
                fvg,
            )
        )

        if evidence_count >= STRONG_EVIDENCE_COUNT:
            return MAX_EVIDENCE_BONUS

        if evidence_count >= (
            MIN_EVIDENCE_FOR_BONUS + 2
        ):
            return 5.0

        if evidence_count >= MIN_EVIDENCE_FOR_BONUS:
            return 2.0

        return 0.0

    @staticmethod
    def _unique_evidence(
        fvg: FairValueGap,
    ) -> list[str]:
        """
        Return unique non-empty evidence while preserving order.
        """

        seen: set[str] = set()
        result: list[str] = []

        evidence = getattr(
            fvg,
            "evidence",
            [],
        )

        if evidence is None:
            return result

        for item in evidence:

            text = str(
                item
            ).strip()

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
        Update the confidence label without creating duplicates.

        Existing confidence labels are removed before the new label is added.
        """

        labels = set(
            self._LABELS.values()
        )

        evidence = getattr(
            fvg,
            "evidence",
            [],
        )

        fvg.evidence = [
            item
            for item in evidence
            if str(item).strip()
            not in labels
        ]

        confidence = self._bounded(
            fvg.confidence,
        )

        if confidence >= EXTREME_QUALITY:
            label = self._LABELS[
                "very_high"
            ]

        elif confidence >= VERY_HIGH_QUALITY:
            label = self._LABELS[
                "very_high"
            ]

        elif confidence >= HIGH_QUALITY:
            label = self._LABELS[
                "high"
            ]

        elif confidence >= 55.0:
            label = self._LABELS[
                "moderate"
            ]

        else:
            label = self._LABELS[
                "low"
            ]

        fvg.evidence.append(
            label
        )

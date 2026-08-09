"""
===============================================================================
COSMOS Volume Confidence Engine

Calculates confidence in the Volume Agent's overall analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.volume.constants import (
    DEFAULT_CONFIDENCE,
    HIGH_CONFIDENCE,
    MAX_CONFIDENCE,
    VERY_HIGH_CONFIDENCE,
)

from ai.agents.volume.models import (
    AccumulationSignal,
    DistributionSignal,
    VolumeConfirmation,
    VolumeDirection,
    VolumeProbability,
    VolumeProfile,
    VolumeSpike,
    VolumeTrend,
)

from ai.agents.volume.utils import normalize_score


class VolumeConfidenceEngine:
    """
    Calculates the reliability/confidence of the combined Volume analysis.

    Confidence considers:

        - confirmation quality
        - probability strength
        - trend agreement
        - accumulation/distribution clarity
        - spike evidence
        - profile quality
        - conflicting evidence

    Confidence does NOT mean probability of profit.
    """

    def analyze(
        self,
        probability: VolumeProbability | None,
        confirmation: VolumeConfirmation | None,
        trend: VolumeTrend | None,
        accumulation: AccumulationSignal | None,
        distribution: DistributionSignal | None,
        profile: VolumeProfile | None,
        spikes: list[VolumeSpike] | None = None,
    ) -> float:

        # =====================================================================
        # NO DATA
        # =====================================================================

        if probability is None:

            return DEFAULT_CONFIDENCE

        confidence = 0.0

        evidence_count = 0

        conflict_count = 0

        # =====================================================================
        # 1. PROBABILITY STRENGTH
        # =====================================================================

        probability_confidence = normalize_score(
            getattr(
                probability,
                "confidence",
                DEFAULT_CONFIDENCE,
            )
        )

        confidence += (
            probability_confidence
            * 0.30
        )

        evidence_count += 1

        # =====================================================================
        # 2. CONFIRMATION
        # =====================================================================

        if confirmation is not None:

            confirmation_score = normalize_score(
                getattr(
                    confirmation,
                    "score",
                    0.0,
                )
            )

            if confirmation.confirmed:

                confidence += (
                    confirmation_score
                    * 0.25
                )

            else:

                confidence += (
                    confirmation_score
                    * 0.10
                )

            evidence_count += 1

            if confirmation.divergence:

                conflict_count += 1

        # =====================================================================
        # 3. TREND
        # =====================================================================

        if trend is not None:

            trend_confidence = normalize_score(
                getattr(
                    trend,
                    "confidence",
                    DEFAULT_CONFIDENCE,
                )
            )

            confidence += (
                trend_confidence
                * 0.15
            )

            evidence_count += 1

        # =====================================================================
        # 4. ACCUMULATION / DISTRIBUTION
        # =====================================================================

        accumulation_detected = (
            accumulation is not None
            and
            accumulation.detected
        )

        distribution_detected = (
            distribution is not None
            and
            distribution.detected
        )

        if accumulation_detected:

            accumulation_confidence = normalize_score(
                accumulation.confidence
            )

            confidence += (
                accumulation_confidence
                * 0.10
            )

            evidence_count += 1

        if distribution_detected:

            distribution_confidence = normalize_score(
                distribution.confidence
            )

            confidence += (
                distribution_confidence
                * 0.10
            )

            evidence_count += 1

        # =====================================================================
        # CONFLICT
        # =====================================================================

        if (
            accumulation_detected
            and
            distribution_detected
        ):

            conflict_count += 1

        # =====================================================================
        # 5. VOLUME SPIKES
        # =====================================================================

        if spikes:

            recent_spikes = spikes[-5:]

            if recent_spikes:

                spike_strengths = [
                    normalize_score(
                        spike.strength
                    )
                    for spike
                    in recent_spikes
                ]

                average_spike_strength = (
                    sum(
                        spike_strengths
                    )
                    /
                    len(
                        spike_strengths
                    )
                )

                confidence += (
                    average_spike_strength
                    * 0.05
                )

                evidence_count += 1

        # =====================================================================
        # 6. PROFILE QUALITY
        # =====================================================================

        if profile is not None:

            profile_confidence = normalize_score(
                getattr(
                    profile,
                    "confidence",
                    0.0,
                )
            )

            confidence += (
                profile_confidence
                * 0.05
            )

            evidence_count += 1

        # =====================================================================
        # 7. CONFLICT PENALTY
        # =====================================================================

        if conflict_count > 0:

            penalty = (
                conflict_count
                * 10.0
            )

            confidence -= penalty

        # =====================================================================
        # 8. EVIDENCE COMPLETENESS
        # =====================================================================

        if evidence_count <= 0:

            confidence = DEFAULT_CONFIDENCE

        else:

            # More independent evidence layers = greater reliability.
            #
            # This is deliberately a modest adjustment so evidence quantity
            # cannot overpower contradictory evidence quality.

            completeness_bonus = min(
                15.0,
                evidence_count
                * 2.0,
            )

            confidence += (
                completeness_bonus
            )

        # =====================================================================
        # 9. FINAL NORMALIZATION
        # =====================================================================

        confidence = normalize_score(
            confidence,
            0.0,
            MAX_CONFIDENCE,
        )

        return round(
            confidence,
            2,
        )

    # =========================================================================
    # CLASSIFICATION
    # =========================================================================

    @staticmethod
    def classify(
        confidence: float,
    ) -> str:
        """
        Convert numeric confidence into a readable classification.
        """

        confidence = normalize_score(
            confidence
        )

        if confidence >= VERY_HIGH_CONFIDENCE:

            return "VERY_HIGH"

        if confidence >= HIGH_CONFIDENCE:

            return "HIGH"

        if confidence >= DEFAULT_CONFIDENCE:

            return "MODERATE"

        return "LOW"
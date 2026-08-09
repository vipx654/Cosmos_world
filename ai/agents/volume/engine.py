"""
===============================================================================
COSMOS Volume Agent

Master orchestration engine for the Volume Agent.

Pipeline:

    Validation
        ↓
    Volume Spike
        ↓
    Volume Trend
        ↓
    Volume Confirmation
        ↓
    Volume Profile
        ↓
    Accumulation
        ↓
    Distribution
        ↓
    Probability
        ↓
    Confidence
        ↓
    Final Volume Result

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.volume.accumulation_engine import (
    AccumulationEngine,
)

from ai.agents.volume.confidence_engine import (
    VolumeConfidenceEngine,
)

from ai.agents.volume.distribution_engine import (
    DistributionEngine,
)

from ai.agents.volume.probability_engine import (
    VolumeProbabilityEngine,
)

from ai.agents.volume.volume_confirmation import (
    VolumeConfirmationEngine,
)

from ai.agents.volume.volume_profile import (
    VolumeProfileEngine,
)

from ai.agents.volume.volume_spike import (
    VolumeSpikeEngine,
)

from ai.agents.volume.volume_trend import (
    VolumeTrendEngine,
)

from ai.agents.volume.validator import (
    VolumeValidator,
)

from ai.agents.volume.models import (
    VolumeAgentResult,
    VolumeDirection,
)


class VolumeEngine:
    """
    Master Volume Agent.

    This class is the only entry point that the rest of COSMOS should need
    during normal operation.

    Individual engines remain independently testable.
    """

    def __init__(self) -> None:

        self.validator = (
            VolumeValidator()
        )

        self.spike_engine = (
            VolumeSpikeEngine()
        )

        self.trend_engine = (
            VolumeTrendEngine()
        )

        self.confirmation_engine = (
            VolumeConfirmationEngine()
        )

        self.profile_engine = (
            VolumeProfileEngine()
        )

        self.accumulation_engine = (
            AccumulationEngine()
        )

        self.distribution_engine = (
            DistributionEngine()
        )

        self.probability_engine = (
            VolumeProbabilityEngine()
        )

        self.confidence_engine = (
            VolumeConfidenceEngine()
        )

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        candles,
    ) -> VolumeAgentResult:
        """
        Run the complete Volume Agent pipeline.
        """

        # =====================================================================
        # 1. VALIDATION
        # =====================================================================

        validation = self.validator.validate(
            candles
        )

        if not validation.valid:

            return VolumeAgentResult(
                direction=(
                    VolumeDirection.NEUTRAL
                ),
                probability=50.0,
                confidence=0.0,
                valid=False,
                evidence=[
                    "Volume data validation failed"
                ],
                validation=validation,
            )

        # =====================================================================
        # 2. VOLUME SPIKES
        # =====================================================================

        spikes = (
            self.spike_engine.analyze(
                candles
            )
        )

        # =====================================================================
        # 3. VOLUME TREND
        # =====================================================================

        trend = (
            self.trend_engine.analyze(
                candles
            )
        )

        # =====================================================================
        # 4. VOLUME CONFIRMATION
        # =====================================================================

        confirmation = (
            self.confirmation_engine.analyze(
                candles,
                spikes,
                trend,
            )
        )

        # =====================================================================
        # 5. VOLUME PROFILE
        # =====================================================================

        profile = (
            self.profile_engine.analyze(
                candles
            )
        )

        # =====================================================================
        # 6. ACCUMULATION
        # =====================================================================

        accumulation = (
            self.accumulation_engine.analyze(
                candles,
                spikes,
                trend,
            )
        )

        # =====================================================================
        # 7. DISTRIBUTION
        # =====================================================================

        distribution = (
            self.distribution_engine.analyze(
                candles,
                spikes,
                trend,
            )
        )

        # =====================================================================
        # 8. PROBABILITY
        # =====================================================================

        probability = (
            self.probability_engine.analyze(
                confirmation=confirmation,
                accumulation=accumulation,
                distribution=distribution,
                trend=trend,
                spikes=spikes,
            )
        )

        # =====================================================================
        # 9. CONFIDENCE
        # =====================================================================

        confidence = (
            self.confidence_engine.analyze(
                probability=probability,
                confirmation=confirmation,
                trend=trend,
                accumulation=accumulation,
                distribution=distribution,
                profile=profile,
                spikes=spikes,
            )
        )

        # =====================================================================
        # 10. BUILD EVIDENCE
        # =====================================================================

        evidence: list[str] = []

        evidence.extend(
            confirmation.reasons
        )

        evidence.extend(
            probability.evidence
        )

        evidence.extend(
            accumulation.evidence
        )

        evidence.extend(
            distribution.evidence
        )

        # Remove duplicate evidence while preserving order.
        evidence = list(
            dict.fromkeys(
                evidence
            )
        )

        # =====================================================================
        # 11. FINAL DIRECTION
        # =====================================================================

        direction = (
            probability.direction
        )

        if direction == VolumeDirection.BULLISH:

            final_probability = (
                probability.bullish_probability
            )

        elif direction == VolumeDirection.BEARISH:

            final_probability = (
                probability.bearish_probability
            )

        else:

            final_probability = (
                probability.neutral_probability
            )

        # =====================================================================
        # 12. FINAL RESULT
        # =====================================================================

        return VolumeAgentResult(

            direction=direction,

            probability=round(
                final_probability,
                2,
            ),

            confidence=round(
                confidence,
                2,
            ),

            valid=True,

            evidence=evidence,

            validation=validation,

            spikes=spikes,

            trend=trend,

            confirmation=confirmation,

            profile=profile,

            accumulation=accumulation,

            distribution=distribution,

            probability_analysis=probability,
        )

    # =========================================================================
    # SAFE ANALYSIS
    # =========================================================================

    def safe_analyze(
        self,
        candles,
    ) -> VolumeAgentResult:
        """
        Safe wrapper used by higher-level COSMOS agents.

        Prevents a malformed data packet from crashing the complete
        multi-agent pipeline.
        """

        try:

            return self.analyze(
                candles
            )

        except Exception as exc:

            return VolumeAgentResult(

                direction=(
                    VolumeDirection.NEUTRAL
                ),

                probability=50.0,

                confidence=0.0,

                valid=False,

                evidence=[
                    "Volume analysis failed",
                    str(exc),
                ],
            )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

volume_engine = VolumeEngine()
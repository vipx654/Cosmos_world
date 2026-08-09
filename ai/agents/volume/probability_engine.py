"""
===============================================================================
COSMOS Volume Probability Engine

Combines volume evidence into directional probability estimates.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.volume.constants import (
    DEFAULT_PROBABILITY,
    HIGH_PROBABILITY,
    MAX_PROBABILITY,
)

from ai.agents.volume.models import (
    AccumulationSignal,
    DistributionSignal,
    VolumeConfirmation,
    VolumeDirection,
    VolumeProbability,
    VolumeSpike,
    VolumeTrend,
)

from ai.agents.volume.utils import normalize_score


class VolumeProbabilityEngine:
    """
    Produces bullish/bearish/neutral probability estimates from the Volume
    Agent's independent evidence layers.

    Important:

        Probability != certainty.

    This represents the directional weight of the volume evidence available
    to COSMOS at the time of analysis.
    """

    def analyze(
        self,
        confirmation: VolumeConfirmation | None,
        accumulation: AccumulationSignal | None,
        distribution: DistributionSignal | None,
        trend: VolumeTrend | None,
        spikes: list[VolumeSpike] | None = None,
    ) -> VolumeProbability:

        # =====================================================================
        # BASE
        # =====================================================================

        bullish_score = 0.0

        bearish_score = 0.0

        evidence: list[str] = []

        # =====================================================================
        # CONFIRMATION
        # =====================================================================

        if confirmation is not None:

            confirmation_score = (
                float(
                    getattr(
                        confirmation,
                        "score",
                        0.0,
                    )
                )
                /
                100.0
            )

            if (
                confirmation.direction
                == VolumeDirection.BULLISH
                and
                confirmation.confirmed
            ):

                bullish_score += (
                    confirmation_score
                    * 35.0
                )

                evidence.append(
                    "Bullish volume confirmation"
                )

            elif (
                confirmation.direction
                == VolumeDirection.BEARISH
                and
                confirmation.confirmed
            ):

                bearish_score += (
                    confirmation_score
                    * 35.0
                )

                evidence.append(
                    "Bearish volume confirmation"
                )

            elif confirmation.divergence:

                evidence.append(
                    "Volume divergence detected"
                )

        # =====================================================================
        # ACCUMULATION
        # =====================================================================

        if (
            accumulation is not None
            and
            accumulation.detected
        ):

            accumulation_score = normalize_score(
                accumulation.confidence
            )

            bullish_score += (
                accumulation_score
                * 0.30
            )

            evidence.append(
                "Accumulation-like evidence supports bullish side"
            )

        # =====================================================================
        # DISTRIBUTION
        # =====================================================================

        if (
            distribution is not None
            and
            distribution.detected
        ):

            distribution_score = normalize_score(
                distribution.confidence
            )

            bearish_score += (
                distribution_score
                * 0.30
            )

            evidence.append(
                "Distribution-like evidence supports bearish side"
            )

        # =====================================================================
        # TREND
        # =====================================================================

        if trend is not None:

            trend_confidence = normalize_score(
                getattr(
                    trend,
                    "confidence",
                    50.0,
                )
            )

            trend_weight = (
                trend_confidence
                * 0.15
            )

            if trend.rising:

                bullish_score += (
                    trend_weight
                )

                evidence.append(
                    "Rising volume activity"
                )

            elif trend.falling:

                bearish_score += (
                    trend_weight
                )

                evidence.append(
                    "Falling volume activity"
                )

        # =====================================================================
        # SPIKES
        # =====================================================================

        if spikes:

            recent_spikes = spikes[-5:]

            bullish_spikes = sum(
                1
                for spike
                in recent_spikes
                if (
                    spike.direction
                    == VolumeDirection.BULLISH
                )
            )

            bearish_spikes = sum(
                1
                for spike
                in recent_spikes
                if (
                    spike.direction
                    == VolumeDirection.BEARISH
                )
            )

            if bullish_spikes > bearish_spikes:

                bullish_score += 10.0

                evidence.append(
                    "Recent bullish volume spikes dominate"
                )

            elif bearish_spikes > bullish_spikes:

                bearish_score += 10.0

                evidence.append(
                    "Recent bearish volume spikes dominate"
                )

        # =====================================================================
        # NORMALIZE
        # =====================================================================

        bullish_score = normalize_score(
            bullish_score
        )

        bearish_score = normalize_score(
            bearish_score
        )

        total_directional_score = (
            bullish_score
            +
            bearish_score
        )

        # =====================================================================
        # NEUTRAL CASE
        # =====================================================================

        if total_directional_score <= 0.0:

            return VolumeProbability(

                direction=(
                    VolumeDirection.NEUTRAL
                ),

                bullish_probability=50.0,

                bearish_probability=50.0,

                neutral_probability=50.0,

                confidence=25.0,

                evidence=[
                    "Insufficient directional volume evidence"
                ],
            )

        # =====================================================================
        # DIRECTIONAL PROBABILITIES
        # =====================================================================

        bullish_probability = (
            bullish_score
            /
            total_directional_score
        ) * 100.0

        bearish_probability = (
            bearish_score
            /
            total_directional_score
        ) * 100.0

        # Neutrality represents uncertainty between the directional evidence.
        directional_gap = abs(
            bullish_probability
            -
            bearish_probability
        )

        neutral_probability = (
            100.0
            -
            directional_gap
        )

        # Keep all values bounded.
        bullish_probability = normalize_score(
            bullish_probability
        )

        bearish_probability = normalize_score(
            bearish_probability
        )

        neutral_probability = normalize_score(
            neutral_probability
        )

        # =====================================================================
        # DIRECTION
        # =====================================================================

        if (
            bullish_probability
            >
            bearish_probability
        ):

            direction = (
                VolumeDirection.BULLISH
            )

        elif (
            bearish_probability
            >
            bullish_probability
        ):

            direction = (
                VolumeDirection.BEARISH
            )

        else:

            direction = (
                VolumeDirection.NEUTRAL
            )

        # =====================================================================
        # PROBABILITY CONFIDENCE
        # =====================================================================

        confidence = normalize_score(
            directional_gap
        )

        if confidence >= HIGH_PROBABILITY:

            evidence.append(
                "Strong directional volume bias"
            )

        elif confidence >= 50.0:

            evidence.append(
                "Moderate directional volume bias"
            )

        else:

            evidence.append(
                "Weak directional volume bias"
            )

        # =====================================================================
        # RETURN
        # =====================================================================

        return VolumeProbability(

            direction=direction,

            bullish_probability=round(
                bullish_probability,
                2,
            ),

            bearish_probability=round(
                bearish_probability,
                2,
            ),

            neutral_probability=round(
                neutral_probability,
                2,
            ),

            confidence=round(
                confidence,
                2,
            ),

            evidence=evidence,
        )
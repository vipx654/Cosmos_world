"""
===============================================================================
COSMOS Sweep Probability Engine

Production probability calculation for detected liquidity sweeps.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.sweep.models import SweepObject


class ProbabilityEngine:
    """
    Calculates the probability score of detected liquidity sweeps.

    V1 factors
    ----------
    Confidence : 60%
    Strength   : 40%

    V2 factors can later include:

    - Trend
    - BOS
    - CHOCH
    - Volume
    - Session
    - FVG
    - Order Block

    The engine intentionally does not reference V2 factors until those
    signals are actually available in the Sweep pipeline.
    """

    CONFIDENCE_WEIGHT = 0.60
    STRENGTH_WEIGHT = 0.40

    MIN_PROBABILITY = 0.0
    MAX_PROBABILITY = 100.0

    def calculate(
        self,
        sweeps: list[SweepObject],
    ) -> list[SweepObject]:
        """
        Calculate and attach probability to every valid sweep.

        The supplied SweepObject instances are enriched in place and
        returned as the same collection.
        """

        if not sweeps:
            return sweeps

        for sweep in sweeps:

            if not isinstance(
                sweep,
                SweepObject,
            ):
                continue

            # -------------------------------------------------------------
            # Normalize source scores first.
            # -------------------------------------------------------------

            confidence = self._clamp_score(
                sweep.confidence
            )

            strength = self._clamp_score(
                sweep.strength
            )

            sweep.confidence = confidence
            sweep.strength = strength

            # -------------------------------------------------------------
            # V1 probability model.
            # -------------------------------------------------------------

            probability = (
                confidence * self.CONFIDENCE_WEIGHT
                +
                strength * self.STRENGTH_WEIGHT
            )

            probability = self._clamp_score(
                probability
            )

            sweep.probability = round(
                probability,
                2,
            )

            # -------------------------------------------------------------
            # Refresh deterministic quality classification.
            # -------------------------------------------------------------

            sweep.clamp_scores()
            sweep.update_quality()

            # -------------------------------------------------------------
            # Evidence.
            # -------------------------------------------------------------

            sweep.add_evidence(
                "Probability Calculated"
            )

        return sweeps

    # =========================================================================
    # SCORE HELPERS
    # =========================================================================

    @classmethod
    def _clamp_score(
        cls,
        value: float,
    ) -> float:
        """
        Clamp a score to the valid 0-100 range.

        Invalid numeric conversion is treated as zero rather than allowing
        malformed upstream data to break the Sweep pipeline.
        """

        try:
            numeric_value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return cls.MIN_PROBABILITY

        if numeric_value != numeric_value:
            return cls.MIN_PROBABILITY

        return max(
            cls.MIN_PROBABILITY,
            min(
                cls.MAX_PROBABILITY,
                numeric_value,
            ),
        )
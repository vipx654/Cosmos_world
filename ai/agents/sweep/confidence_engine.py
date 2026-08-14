"""
===============================================================================
COSMOS Sweep Confidence Engine

Production confidence calculation for detected liquidity sweeps.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.sweep.models import SweepObject


class ConfidenceEngine:
    """
    Calculates institutional confidence for liquidity sweeps.

    V1 factors
    ----------
    Sweep Strength : 50%
    Probability    : 50%

    V2 factors
    ----------
    Trend
    Volume
    Session
    BOS
    CHOCH
    FVG
    Order Block

    V2 factors are intentionally excluded until their signals are available
    as reliable upstream inputs.
    """

    STRENGTH_WEIGHT = 0.50
    PROBABILITY_WEIGHT = 0.50

    MIN_SCORE = 0.0
    MAX_SCORE = 100.0

    def calculate(
        self,
        sweeps: list[SweepObject],
    ) -> float:
        """
        Calculate confidence for all valid sweeps.

        Each SweepObject is enriched in place.

        Returns
        -------
        float
            Average confidence across valid sweeps.
        """

        if not sweeps:
            return 0.0

        total = 0.0
        valid_count = 0

        for sweep in sweeps:

            if not isinstance(
                sweep,
                SweepObject,
            ):
                continue

            strength = self._clamp_score(
                sweep.strength
            )

            probability = self._clamp_score(
                sweep.probability
            )

            # -------------------------------------------------------------
            # Normalize source values before calculation.
            # -------------------------------------------------------------

            sweep.strength = strength
            sweep.probability = probability

            # -------------------------------------------------------------
            # V1 confidence model.
            # -------------------------------------------------------------

            confidence = (
                strength * self.STRENGTH_WEIGHT
                +
                probability * self.PROBABILITY_WEIGHT
            )

            confidence = self._clamp_score(
                confidence
            )

            sweep.confidence = round(
                confidence,
                2,
            )

            # -------------------------------------------------------------
            # Keep the model's quality classification synchronized.
            # -------------------------------------------------------------

            sweep.clamp_scores()
            sweep.update_quality()

            # -------------------------------------------------------------
            # Evidence.
            # -------------------------------------------------------------

            sweep.add_evidence(
                "Confidence Calculated"
            )

            total += sweep.confidence
            valid_count += 1

        if valid_count == 0:
            return 0.0

        return round(
            total / valid_count,
            2,
        )

    # =========================================================================
    # SCORE VALIDATION
    # =========================================================================

    @classmethod
    def _clamp_score(
        cls,
        value: float,
    ) -> float:
        """
        Safely normalize a score into the 0-100 range.

        Invalid or non-finite values are treated as zero so malformed
        upstream data cannot corrupt the Sweep pipeline.
        """

        try:
            numeric_value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return cls.MIN_SCORE

        if not (
            numeric_value == numeric_value
        ):
            return cls.MIN_SCORE

        if numeric_value == float("inf"):
            return cls.MAX_SCORE

        if numeric_value == float("-inf"):
            return cls.MIN_SCORE

        return max(
            cls.MIN_SCORE,
            min(
                cls.MAX_SCORE,
                numeric_value,
            ),
        )
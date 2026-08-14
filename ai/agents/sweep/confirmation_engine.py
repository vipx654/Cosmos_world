"""
===============================================================================
COSMOS Sweep Confirmation Engine

Production confirmation layer for institutional liquidity sweeps.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.sweep.models import (
    SweepObject,
    SweepStatus,
)


class ConfirmationEngine:
    """
    Confirms detected liquidity sweeps using deterministic evidence scoring.

    V1 confirmation factors
    -----------------------
    - Confidence
    - Probability
    - Strength

    A sweep is confirmed when at least two of the three factors meet the
    confirmation threshold.

    Invalid, failed, or previously identified fake sweeps are never confirmed.

    Future versions can extend the scoring model with:

    - BOS
    - CHOCH
    - FVG
    - Order Block
    - Trend
    - Volume
    - Session
    - Liquidity Density
    """

    CONFIRMATION_THRESHOLD = 70.0
    MIN_CONFIRMATION_FACTORS = 2

    def analyze(
        self,
        sweeps: list[SweepObject],
    ) -> list[SweepObject]:
        """
        Confirm valid sweeps.

        The method mutates the existing SweepObject instances so downstream
        pipeline stages retain the same objects and their accumulated evidence.
        """

        if not sweeps:
            return []

        confirmed: list[SweepObject] = []

        for sweep in sweeps:

            if not isinstance(
                sweep,
                SweepObject,
            ):
                continue

            # ---------------------------------------------------------------
            # Normalize scores before evaluation.
            # ---------------------------------------------------------------

            sweep.clamp_scores()

            # ---------------------------------------------------------------
            # Do not confirm terminal or explicitly invalidated sweeps.
            # ---------------------------------------------------------------

            if sweep.status in (
                SweepStatus.FAILED,
                SweepStatus.INVALID,
            ):
                continue

            # ---------------------------------------------------------------
            # Fake sweeps are intentionally excluded from confirmation.
            # ---------------------------------------------------------------

            if sweep.fake:
                continue

            # ---------------------------------------------------------------
            # V1 evidence scoring.
            # ---------------------------------------------------------------

            score = 0

            if (
                sweep.confidence
                >= self.CONFIRMATION_THRESHOLD
            ):
                score += 1

            if (
                sweep.probability
                >= self.CONFIRMATION_THRESHOLD
            ):
                score += 1

            if (
                sweep.strength
                >= self.CONFIRMATION_THRESHOLD
            ):
                score += 1

            # ---------------------------------------------------------------
            # Confirmation decision.
            # ---------------------------------------------------------------

            if score < self.MIN_CONFIRMATION_FACTORS:
                continue

            # ---------------------------------------------------------------
            # Update lifecycle state.
            # ---------------------------------------------------------------

            sweep.status = SweepStatus.CONFIRMED

            sweep.add_evidence(
                "Sweep Confirmed"
            )

            sweep.add_evidence(
                "Confirmation Threshold Met"
            )

            confirmed.append(sweep)

        return confirmed
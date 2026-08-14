"""
===============================================================================
COSMOS Fake Sweep Engine

Production fake-liquidity-sweep classification.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.sweep.models import (
    SweepObject,
    SweepStatus,
)


class FakeSweepEngine:
    """
    Classifies detected sweeps that currently lack sufficient evidence.

    The Fake Sweep Engine does NOT confirm a sweep.

    Lifecycle:

        DETECTED
            ↓
        PENDING
            ↓
        Fake Sweep classification
            ↓
        Confirmation Engine
            ↓
        CONFIRMED / FAILED

    V1 evidence:

    • Confidence
    • Probability
    • Strength
    • Confirmation state

    V2 can additionally incorporate:

    • BOS
    • CHOCH
    • Volume
    • FVG
    • Order Block
    • Trend
    • Session
    """

    MIN_CONFIDENCE = 70.0
    MIN_PROBABILITY = 70.0
    MIN_STRENGTH = 70.0

    REQUIRED_WEAK_FACTORS = 2

    def analyze(
        self,
        sweeps: list[SweepObject],
    ) -> list[SweepObject]:
        """
        Return sweeps that currently qualify as possible fake sweeps.

        A sweep is considered a possible fake when at least two of the
        three primary V1 quality metrics are below their minimum thresholds.

        Confirmed sweeps are never downgraded to fake by this engine.
        """

        if not sweeps:
            return []

        fake_sweeps: list[SweepObject] = []

        for sweep in sweeps:

            if not isinstance(
                sweep,
                SweepObject,
            ):
                continue

            # -------------------------------------------------------------
            # Do not downgrade an already confirmed sweep.
            # -------------------------------------------------------------

            if sweep.status is SweepStatus.CONFIRMED:
                continue

            # -------------------------------------------------------------
            # Already classified as fake.
            # -------------------------------------------------------------

            if sweep.fake:
                sweep.add_evidence(
                    "Possible Fake Sweep"
                )

                fake_sweeps.append(
                    sweep
                )

                continue

            # -------------------------------------------------------------
            # Evaluate V1 evidence.
            # -------------------------------------------------------------

            weak_factors = 0

            if sweep.confidence < self.MIN_CONFIDENCE:
                weak_factors += 1

            if sweep.probability < self.MIN_PROBABILITY:
                weak_factors += 1

            if sweep.strength < self.MIN_STRENGTH:
                weak_factors += 1

            # -------------------------------------------------------------
            # Classify.
            # -------------------------------------------------------------

            if weak_factors < self.REQUIRED_WEAK_FACTORS:
                continue

            sweep.fake = True

            sweep.add_evidence(
                "Possible Fake Sweep"
            )

            fake_sweeps.append(
                sweep
            )

        return fake_sweeps
"""
===============================================================================
COSMOS Fair Value Gap Probability Engine

Calculates a normalized probability score for detected Fair Value Gaps.

Important:
    This is a V1 heuristic probability score, NOT a statistically validated
    win probability. It should be calibrated later using backtest data.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.constants import (
    MAX_PROBABILITY,
    MIN_PROBABILITY,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGDirection,
    FVGStatus,
    InversionStatus,
)


class ProbabilityEngine:
    """
    Calculates FVG probability using available structural evidence.

    V1 factors:

    - Base FVG quality
    - Confidence
    - Strength
    - Freshness
    - Mitigation state
    - Inversion state
    - Directional validity

    V2 can additionally consume:

    - Liquidity sweep
    - BOS / CHOCH
    - Order Block overlap
    - Trend
    - Volume
    - Session
    - HTF alignment
    - Liquidity density
    - Historical backtest statistics
    """

    def analyze(
        self,
        fvgs: list[FairValueGap],
    ) -> list[FairValueGap]:

        if not fvgs:
            return []

        for fvg in fvgs:

            score = 50.0

            # =============================================================
            # CONFIDENCE CONTRIBUTION
            # =============================================================

            confidence = max(
                0.0,
                min(
                    100.0,
                    float(
                        fvg.confidence
                    ),
                ),
            )

            score += (
                confidence
                - 50.0
            ) * 0.20

            # =============================================================
            # STRENGTH CONTRIBUTION
            # =============================================================

            strength = max(
                0.0,
                min(
                    100.0,
                    float(
                        fvg.strength
                    ),
                ),
            )

            score += (
                strength
                - 50.0
            ) * 0.20

            # =============================================================
            # EXISTING PROBABILITY CONTRIBUTION
            # =============================================================

            existing_probability = max(
                0.0,
                min(
                    100.0,
                    float(
                        fvg.probability
                    ),
                ),
            )

            score += (
                existing_probability
                - 50.0
            ) * 0.10

            # =============================================================
            # FRESHNESS
            # =============================================================

            if fvg.status == FVGStatus.FRESH:

                score += 10.0

            elif fvg.status == FVGStatus.PARTIAL:

                score += 4.0

            elif fvg.status == FVGStatus.TESTED:

                score -= 2.0

            elif fvg.status == FVGStatus.FILLED:

                score -= 20.0

            elif fvg.status == FVGStatus.INVALID:

                score -= 30.0

            # =============================================================
            # INVERSION
            # =============================================================

            if (
                fvg.inversion_status
                == InversionStatus.CONFIRMED
            ):

                # An inverted FVG is still potentially useful, but its
                # original directional thesis is no longer active.

                score -= 5.0

            elif (
                fvg.inversion_status
                == InversionStatus.POTENTIAL
            ):

                score -= 2.0

            # =============================================================
            # DIRECTION
            # =============================================================

            if fvg.direction in (
                FVGDirection.BULLISH,
                FVGDirection.BEARISH,
            ):

                score += 5.0

            else:

                score -= 10.0

            # =============================================================
            # EVIDENCE QUALITY
            # =============================================================

            evidence_count = len(
                fvg.evidence
            )

            if evidence_count >= 4:

                score += 8.0

            elif evidence_count >= 2:

                score += 4.0

            # =============================================================
            # NORMALIZE
            # =============================================================

            score = max(
                MIN_PROBABILITY,
                min(
                    MAX_PROBABILITY,
                    score,
                ),
            )

            fvg.probability = round(
                score,
                2,
            )

            # =============================================================
            # ADD EVIDENCE LABEL
            # =============================================================

            if fvg.probability >= 80.0:

                if (
                    "High FVG Probability"
                    not in fvg.evidence
                ):

                    fvg.evidence.append(
                        "High FVG Probability"
                    )

            elif fvg.probability >= 65.0:

                if (
                    "Moderate FVG Probability"
                    not in fvg.evidence
                ):

                    fvg.evidence.append(
                        "Moderate FVG Probability"
                    )

            else:

                if (
                    "Low FVG Probability"
                    not in fvg.evidence
                ):

                    fvg.evidence.append(
                        "Low FVG Probability"
                    )

        return fvgs
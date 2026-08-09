"""
===============================================================================
COSMOS Fair Value Gap Confirmation Engine

Evaluates supporting evidence around detected Fair Value Gaps.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.constants import (
    MIN_CONFIRMATION_SCORE,
    STRONG_CONFIRMATION_SCORE,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGConfirmation,
    FVGDirection,
    FVGStatus,
)


class ConfirmationEngine:
    """
    Confirms FVG quality using available evidence.

    V1 confirmation signals:

    - FVG is valid
    - FVG is fresh or partially mitigated
    - FVG has meaningful confidence
    - FVG has meaningful probability
    - FVG has meaningful strength

    The engine is intentionally tolerant of missing optional market-context
    fields. Future versions can add:

    - BOS
    - CHOCH
    - liquidity sweep
    - order block
    - trend
    - volume
    - session
    - liquidity density
    """

    def analyze(
        self,
        fvgs: list[FairValueGap],
    ) -> list[FVGConfirmation]:

        confirmations: list[FVGConfirmation] = []

        if not fvgs:
            return confirmations

        for fvg in fvgs:

            score = 0

            reasons: list[str] = []

            # -----------------------------------------------------------------
            # Basic validity
            # -----------------------------------------------------------------

            if not fvg.valid:

                confirmations.append(
                    FVGConfirmation(
                        fvg=fvg,
                        confirmed=False,
                        score=0.0,
                        reasons=[
                            "FVG Invalid"
                        ],
                    )
                )

                continue

            score += 1

            reasons.append(
                "FVG Valid"
            )

            # -----------------------------------------------------------------
            # Fresh / partially mitigated zones are still actionable.
            # Fully filled zones are not confirmed as active FVGs.
            # -----------------------------------------------------------------

            if fvg.status in (
                FVGStatus.FRESH,
                FVGStatus.PARTIAL,
            ):

                score += 1

                reasons.append(
                    "FVG Remains Active"
                )

            elif fvg.status == FVGStatus.FILLED:

                reasons.append(
                    "FVG Fully Filled"
                )

            # -----------------------------------------------------------------
            # Confidence
            # -----------------------------------------------------------------

            if fvg.confidence >= 70.0:

                score += 1

                reasons.append(
                    "High Confidence"
                )

            # -----------------------------------------------------------------
            # Probability
            # -----------------------------------------------------------------

            if fvg.probability >= 70.0:

                score += 1

                reasons.append(
                    "High Probability"
                )

            # -----------------------------------------------------------------
            # Strength
            # -----------------------------------------------------------------

            if fvg.strength >= 70.0:

                score += 1

                reasons.append(
                    "Strong FVG"
                )

            # -----------------------------------------------------------------
            # Direction must be recognized.
            # -----------------------------------------------------------------

            if fvg.direction in (
                FVGDirection.BULLISH,
                FVGDirection.BEARISH,
            ):

                reasons.append(
                    f"{fvg.direction.value} Direction"
                )

            # -----------------------------------------------------------------
            # Final confirmation.
            # -----------------------------------------------------------------

            confirmed = (
                score >= MIN_CONFIRMATION_SCORE
                and
                fvg.status != FVGStatus.FILLED
                and
                fvg.valid
            )

            if score >= STRONG_CONFIRMATION_SCORE:

                reasons.append(
                    "Strong Confirmation"
                )

            elif confirmed:

                reasons.append(
                    "FVG Confirmed"
                )

            else:

                reasons.append(
                    "Insufficient Confirmation"
                )

            confirmation = FVGConfirmation(

                fvg=fvg,

                confirmed=confirmed,

                score=float(score),

                reasons=reasons,

            )

            if confirmed:

                fvg.evidence.append(
                    "FVG Confirmed"
                )

            confirmations.append(
                confirmation
            )

        return confirmations
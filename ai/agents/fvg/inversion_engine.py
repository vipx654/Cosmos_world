"""
===============================================================================
COSMOS Fair Value Gap Inversion Engine

Detects Inversion Fair Value Gaps (IFVGs).

An FVG becomes an inversion when price closes through the original imbalance
and the original directional premise is invalidated.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.constants import (
    MIN_INVERSION_CONFIRMATION_CANDLES,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGDirection,
    FVGInversionResult,
    InversionStatus,
)

from ai.agents.fvg.utils import (
    opposite_direction,
)


class InversionEngine:
    """
    Detects FVG role reversals.

    Bullish FVG:
        Close below the FVG -> bearish inversion.

    Bearish FVG:
        Close above the FVG -> bullish inversion.

    V1 uses candle CLOSE as the confirmation mechanism. This is intentionally
    stricter than wick-only invalidation.
    """

    def analyze(
        self,
        fvgs: list[FairValueGap],
        candles,
    ) -> list[FVGInversionResult]:

        results: list[FVGInversionResult] = []

        if not fvgs or not candles:
            return results

        for fvg in fvgs:

            # Already inverted.
            if fvg.inverted:

                results.append(
                    FVGInversionResult(
                        fvg=fvg,
                        status=(
                            InversionStatus.CONFIRMED
                        ),
                        inverted=True,
                        new_direction=(
                            fvg.direction
                        ),
                        evidence=[
                            "FVG Already Inverted"
                        ],
                    )
                )

                continue

            inversion_count = 0

            inversion_confirmed = False

            evidence: list[str] = []

            new_direction = (
                fvg.direction
            )

            start_index = (
                fvg.third_candle_index + 1
            )

            # -------------------------------------------------------------
            # Examine candles after FVG formation.
            # -------------------------------------------------------------

            for candle in candles[start_index:]:

                close = float(
                    candle.close
                )

                # ---------------------------------------------------------
                # Bullish FVG failure:
                #
                # Price closes below the lower boundary.
                # Former support becomes potential resistance.
                # ---------------------------------------------------------

                if (
                    fvg.direction
                    == FVGDirection.BULLISH
                    and
                    close < float(fvg.low)
                ):

                    inversion_count += 1

                    if (
                        inversion_count
                        >= MIN_INVERSION_CONFIRMATION_CANDLES
                    ):

                        inversion_confirmed = True

                        new_direction = (
                            FVGDirection.BEARISH
                        )

                        evidence.append(
                            "Bullish FVG Broken"
                        )

                        evidence.append(
                            "Close Below FVG"
                        )

                        break

                # ---------------------------------------------------------
                # Bearish FVG failure:
                #
                # Price closes above the upper boundary.
                # Former resistance becomes potential support.
                # ---------------------------------------------------------

                elif (
                    fvg.direction
                    == FVGDirection.BEARISH
                    and
                    close > float(fvg.high)
                ):

                    inversion_count += 1

                    if (
                        inversion_count
                        >= MIN_INVERSION_CONFIRMATION_CANDLES
                    ):

                        inversion_confirmed = True

                        new_direction = (
                            FVGDirection.BULLISH
                        )

                        evidence.append(
                            "Bearish FVG Broken"
                        )

                        evidence.append(
                            "Close Above FVG"
                        )

                        break

            # -------------------------------------------------------------
            # Apply inversion state.
            # -------------------------------------------------------------

            if inversion_confirmed:

                fvg.inverted = True

                fvg.inversion_status = (
                    InversionStatus.CONFIRMED
                )

                fvg.fvg_type = (
                    fvg.fvg_type
                )

                fvg.direction = (
                    new_direction
                )

                fvg.valid = True

                fvg.evidence.extend(
                    evidence
                )

                result = FVGInversionResult(

                    fvg=fvg,

                    status=(
                        InversionStatus.CONFIRMED
                    ),

                    inverted=True,

                    new_direction=new_direction,

                    evidence=evidence,

                )

            else:

                result = FVGInversionResult(

                    fvg=fvg,

                    status=(
                        InversionStatus.NONE
                    ),

                    inverted=False,

                    new_direction=(
                        opposite_direction(
                            fvg.direction
                        )
                        if False
                        else fvg.direction
                    ),

                    evidence=[
                        "No Confirmed Inversion"
                    ],

                )

            results.append(
                result
            )

        return results
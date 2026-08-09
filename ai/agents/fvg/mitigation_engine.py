"""
===============================================================================
COSMOS Fair Value Gap Mitigation Engine

Tracks how price interacts with previously detected Fair Value Gaps.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.models import (
    FairValueGap,
    FVGMitigationResult,
    MitigationStatus,
)

from ai.agents.fvg.utils import (
    apply_fill_to_fvg,
    calculate_fill_ratio,
    candle_touches_fvg,
)


class MitigationEngine:
    """
    Determines whether an FVG is:

    - Untouched
    - Partially filled
    - Fully filled

    V1 deliberately tracks price interaction using candle ranges.
    More advanced V2 logic can incorporate:

    - Candle closes
    - CE reactions
    - displacement
    - volume
    - session
    - structure
    - multi-timeframe confluence
    """

    def analyze(
        self,
        fvgs: list[FairValueGap],
        candles,
    ) -> list[FVGMitigationResult]:

        results: list[FVGMitigationResult] = []

        if not fvgs or not candles:
            return results

        for fvg in fvgs:

            best_fill = fvg.fill_ratio

            touched = False

            evidence: list[str] = []

            # -----------------------------------------------------------------
            # Only inspect candles formed after the FVG itself.
            # -----------------------------------------------------------------

            start_index = (
                fvg.third_candle_index + 1
            )

            for candle in candles[start_index:]:

                if not candle_touches_fvg(
                    candle,
                    fvg,
                ):
                    continue

                touched = True

                fill_ratio = (
                    calculate_fill_ratio(
                        candle,
                        fvg,
                    )
                )

                if fill_ratio > best_fill:
                    best_fill = fill_ratio

            # -----------------------------------------------------------------
            # Update FVG state.
            # -----------------------------------------------------------------

            if touched:

                fvg.mitigation_count += 1

                apply_fill_to_fvg(
                    fvg,
                    best_fill,
                )

                if (
                    fvg.mitigation_status
                    == MitigationStatus.PARTIAL
                ):

                    evidence.append(
                        "FVG Partially Mitigated"
                    )

                elif (
                    fvg.mitigation_status
                    == MitigationStatus.FULL
                ):

                    evidence.append(
                        "FVG Fully Mitigated"
                    )

                else:

                    evidence.append(
                        "FVG Tested"
                    )

            else:

                fvg.mitigation_status = (
                    MitigationStatus.UNTOUCHED
                )

                evidence.append(
                    "FVG Untouched"
                )

            # -----------------------------------------------------------------
            # Create result.
            # -----------------------------------------------------------------

            result = FVGMitigationResult(

                fvg=fvg,

                status=fvg.mitigation_status,

                fill_ratio=round(
                    fvg.fill_ratio,
                    4,
                ),

                touched=touched,

                partially_filled=(
                    fvg.mitigation_status
                    == MitigationStatus.PARTIAL
                ),

                fully_filled=(
                    fvg.mitigation_status
                    == MitigationStatus.FULL
                ),

                invalidated=(
                    fvg.mitigation_status
                    == MitigationStatus.INVALIDATED
                ),

                evidence=evidence,

            )

            fvg.evidence.extend(
                evidence
            )

            results.append(
                result
            )

        return results
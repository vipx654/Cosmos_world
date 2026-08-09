"""
===============================================================================
COSMOS Fair Value Gap Map

Organizes detected FVGs into directional and lifecycle-based collections.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.models import (
    FairValueGap,
    FVGMap,
    FVGStatus,
    FVGDirection,
    InversionStatus,
    MitigationStatus,
)


class FVGMapEngine:
    """
    Builds an organized FVGMap from a collection of FVG objects.
    """

    def build(
        self,
        fvgs: list[FairValueGap],
    ) -> FVGMap:

        bullish: list[FairValueGap] = []

        bearish: list[FairValueGap] = []

        inverted: list[FairValueGap] = []

        mitigated: list[FairValueGap] = []

        fresh: list[FairValueGap] = []

        tested: list[FairValueGap] = []

        partial: list[FairValueGap] = []

        filled: list[FairValueGap] = []

        invalid: list[FairValueGap] = []

        # ---------------------------------------------------------------------
        # Classify every FVG.
        # ---------------------------------------------------------------------

        for fvg in fvgs:

            # Direction
            if fvg.direction == FVGDirection.BULLISH:

                bullish.append(fvg)

            elif fvg.direction == FVGDirection.BEARISH:

                bearish.append(fvg)

            # Inversion
            if (
                fvg.inverted
                or
                fvg.inversion_status
                == InversionStatus.CONFIRMED
            ):

                inverted.append(fvg)

            # Mitigation
            if (
                fvg.mitigation_status
                in (
                    MitigationStatus.PARTIAL,
                    MitigationStatus.FULL,
                )
            ):

                mitigated.append(fvg)

            # Lifecycle
            if fvg.status == FVGStatus.FRESH:

                fresh.append(fvg)

            elif fvg.status == FVGStatus.TESTED:

                tested.append(fvg)

            elif fvg.status == FVGStatus.PARTIAL:

                partial.append(fvg)

            elif fvg.status == FVGStatus.FILLED:

                filled.append(fvg)

            elif fvg.status == FVGStatus.INVALID:

                invalid.append(fvg)

        return FVGMap(
            bullish=bullish,
            bearish=bearish,
            inverted=inverted,
            mitigated=mitigated,
            fresh=fresh,
            tested=tested,
            partial=partial,
            filled=filled,
            invalid=invalid,
            all_fvgs=list(fvgs),
        )
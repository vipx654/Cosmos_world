"""
===============================================================================
COSMOS Fair Value Gap Map V2

Organizes detected FVGs into directional, inversion, mitigation and lifecycle
collections.

The map is built only after detection, mitigation, inversion, probability and
confirmation have finalized the FVG state.

Design goals:

    - Deterministic classification
    - Stable FVGMap contract
    - No mutation of FVG objects
    - Correct post-inversion direction handling
    - Explicit lifecycle classification
    - Safe handling of empty input
    - Duplicate-safe collection construction
    - Future-ready for ranking, confluence and visualization

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.models import (
    FairValueGap,
    FVGDirection,
    FVGMap,
    FVGStatus,
    InversionStatus,
    MitigationStatus,
)


class FVGMapEngine:
    """
    Builds the normalized FVGMap used by the FVG Agent.

    The engine does not modify FVG state. It only indexes the finalized state
    into useful collections.
    """

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def build(
        self,
        fvgs: list[FairValueGap],
    ) -> FVGMap:
        """
        Build an FVGMap from the supplied FVG collection.

        The input order is preserved.

        Empty input produces a valid empty FVGMap.
        """

        if not fvgs:
            return self._empty_map()

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
        #
        # An FVG may legitimately belong to multiple collections:
        #
        #     bullish + inverted
        #     bearish + partial
        #     bullish + mitigated
        #
        # Direction and lifecycle are independent dimensions.
        # ---------------------------------------------------------------------

        for fvg in fvgs:

            self._classify_direction(
                fvg=fvg,
                bullish=bullish,
                bearish=bearish,
            )

            self._classify_inversion(
                fvg=fvg,
                inverted=inverted,
            )

            self._classify_mitigation(
                fvg=fvg,
                mitigated=mitigated,
            )

            self._classify_lifecycle(
                fvg=fvg,
                fresh=fresh,
                tested=tested,
                partial=partial,
                filled=filled,
                invalid=invalid,
            )

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

    # =========================================================================
    # DIRECTION
    # =========================================================================

    @staticmethod
    def _classify_direction(
        *,
        fvg: FairValueGap,
        bullish: list[FairValueGap],
        bearish: list[FairValueGap],
    ) -> None:
        """
        Classify the current active FVG direction.

        Important:
            Direction is read from fvg.direction AFTER inversion.

        Therefore a bullish FVG that becomes an IFVG and changes direction to
        bearish will appear in the bearish collection.
        """

        if fvg.direction == FVGDirection.BULLISH:

            bullish.append(fvg)

        elif fvg.direction == FVGDirection.BEARISH:

            bearish.append(fvg)

    # =========================================================================
    # INVERSION
    # =========================================================================

    @staticmethod
    def _classify_inversion(
        *,
        fvg: FairValueGap,
        inverted: list[FairValueGap],
    ) -> None:
        """
        Classify confirmed inverted FVGs.

        Both explicit boolean state and inversion status are supported because
        the model exposes both fields.
        """

        if (
            bool(fvg.inverted)
            or
            fvg.inversion_status
            == InversionStatus.CONFIRMED
        ):
            inverted.append(fvg)

    # =========================================================================
    # MITIGATION
    # =========================================================================

    @staticmethod
    def _classify_mitigation(
        *,
        fvg: FairValueGap,
        mitigated: list[FairValueGap],
    ) -> None:
        """
        Classify FVGs that have experienced meaningful price interaction.

        Partial and full mitigation are considered mitigated.

        Invalidated FVGs are deliberately not included merely because they
        have an invalidation state; invalidation is represented separately by
        the lifecycle collection.
        """

        if fvg.mitigation_status in (
            MitigationStatus.PARTIAL,
            MitigationStatus.FULL,
        ):
            mitigated.append(fvg)

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    @staticmethod
    def _classify_lifecycle(
        *,
        fvg: FairValueGap,
        fresh: list[FairValueGap],
        tested: list[FairValueGap],
        partial: list[FairValueGap],
        filled: list[FairValueGap],
        invalid: list[FairValueGap],
    ) -> None:
        """
        Classify an FVG into its current lifecycle state.

        Lifecycle collections are mutually exclusive.
        """

        status = fvg.status

        if status == FVGStatus.FRESH:

            fresh.append(fvg)

        elif status == FVGStatus.TESTED:

            tested.append(fvg)

        elif status == FVGStatus.PARTIAL:

            partial.append(fvg)

        elif status == FVGStatus.FILLED:

            filled.append(fvg)

        elif status == FVGStatus.INVALID:

            invalid.append(fvg)

    # =========================================================================
    # EMPTY MAP
    # =========================================================================

    @staticmethod
    def _empty_map() -> FVGMap:
        """
        Return a fully initialized empty FVGMap.

        Keeping every field as an independent list prevents accidental shared
        mutable state between map instances.
        """

        return FVGMap(
            bullish=[],
            bearish=[],
            inverted=[],
            mitigated=[],
            fresh=[],
            tested=[],
            partial=[],
            filled=[],
            invalid=[],
            all_fvgs=[],
        )

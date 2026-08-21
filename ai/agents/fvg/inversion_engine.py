"""
===============================================================================
COSMOS Fair Value Gap Inversion Engine V2

Detects and confirms Inversion Fair Value Gaps (IFVGs).

An FVG becomes an inversion when price invalidates the original directional
imbalance and confirms a role reversal through candle closes.

Pipeline role:

    FVG Detection
         ↓
    Mitigation
         ↓
    Inversion Detection
         ↓
    Probability / Confidence
         ↓
    Confirmation

Design goals:

    - Deterministic inversion detection
    - Close-based confirmation
    - Consecutive confirmation support
    - Potential inversion state
    - Confirmed inversion state
    - Correct directional reversal
    - No duplicate inversion mutation
    - Stable result contract
    - Full evidence tracking
    - Future-ready for:
        * BOS / CHOCH
        * liquidity sweeps
        * displacement
        * volume
        * HTF confirmation
        * session context
        * adaptive IFVG scoring

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.constants import (
    INVERSION_CONFIRMATION_RATIO,
    INVERSION_CLOSE_BUFFER_RATIO,
    MAX_INVERSION_CONFIRMATION_CANDLES,
    MIN_INVERSION_CONFIRMATION_CANDLES,
    STRONG_INVERSION_CONFIRMATION_CANDLES,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGDirection,
    FVGInversionResult,
    InversionStatus,
)

from ai.agents.fvg.utils import (
    gap_range,
    opposite_direction,
)


class InversionEngine:
    """
    Detects Fair Value Gap inversions.

    Bullish FVG
        Price closes below the FVG lower boundary.
        Original bullish support thesis becomes bearish.

    Bearish FVG
        Price closes above the FVG upper boundary.
        Original bearish resistance thesis becomes bullish.

    Confirmation is close-based rather than wick-based.

    The engine supports:

        NONE
        POTENTIAL
        CONFIRMED

    A confirmed inversion changes the active FVG direction while preserving
    the original FVG type for historical traceability.
    """

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        fvgs: list[FairValueGap],
        candles,
    ) -> list[FVGInversionResult]:
        """
        Analyze all detected FVGs for inversion.

        Args:
            fvgs:
                Detected FVG objects.

            candles:
                Market candle collection.

        Returns:
            One FVGInversionResult per supplied FVG.
        """

        results: list[FVGInversionResult] = []

        if not fvgs or not candles:
            return results

        for fvg in fvgs:
            result = self._analyze_single(
                fvg,
                candles,
            )

            results.append(result)

        return results

    # =========================================================================
    # SINGLE FVG ANALYSIS
    # =========================================================================

    def _analyze_single(
        self,
        fvg: FairValueGap,
        candles,
    ) -> FVGInversionResult:
        """
        Analyze one FVG for inversion.
        """

        # ---------------------------------------------------------------------
        # Already confirmed.
        #
        # Never re-process an already inverted FVG.
        # ---------------------------------------------------------------------

        if (
            fvg.inverted
            or
            fvg.inversion_status
            == InversionStatus.CONFIRMED
        ):
            return FVGInversionResult(
                fvg=fvg,
                status=InversionStatus.CONFIRMED,
                inverted=True,
                new_direction=fvg.direction,
                evidence=[
                    "FVG Already Inverted",
                    f"Active Direction: {fvg.direction.value}",
                ],
            )

        # ---------------------------------------------------------------------
        # Basic validation.
        # ---------------------------------------------------------------------

        if fvg.high <= fvg.low:
            return FVGInversionResult(
                fvg=fvg,
                status=InversionStatus.NONE,
                inverted=False,
                new_direction=fvg.direction,
                evidence=[
                    "Invalid FVG Price Range",
                ],
            )

        start_index = (
            fvg.third_candle_index + 1
        )

        if start_index >= len(candles):
            return FVGInversionResult(
                fvg=fvg,
                status=InversionStatus.NONE,
                inverted=False,
                new_direction=fvg.direction,
                evidence=[
                    "No Post-Formation Candles Available",
                ],
            )

        # ---------------------------------------------------------------------
        # Determine confirmation requirements.
        # ---------------------------------------------------------------------

        required_confirmations = self._confirmation_requirement()

        consecutive_breaks = 0
        maximum_breaks = 0
        potential_detected = False

        evidence: list[str] = []

        new_direction = fvg.direction

        # ---------------------------------------------------------------------
        # Close buffer.
        #
        # A zero buffer preserves current behaviour.
        #
        # For bullish FVG:
        #     close < low - buffer
        #
        # For bearish FVG:
        #     close > high + buffer
        # ---------------------------------------------------------------------

        buffer = self._close_buffer(
            fvg
        )

        # ---------------------------------------------------------------------
        # Examine candles after FVG formation.
        # ---------------------------------------------------------------------

        for candle in candles[start_index:]:

            close = float(
                candle.close
            )

            broken = self._is_boundary_broken(
                fvg=fvg,
                close=close,
                buffer=buffer,
            )

            if broken:

                potential_detected = True

                consecutive_breaks += 1

                maximum_breaks = max(
                    maximum_breaks,
                    consecutive_breaks,
                )

                if (
                    consecutive_breaks
                    >= required_confirmations
                ):
                    new_direction = (
                        opposite_direction(
                            fvg.direction
                        )
                    )

                    evidence.extend(
                        self._confirmation_evidence(
                            fvg=fvg,
                            confirmation_count=(
                                consecutive_breaks
                            ),
                        )
                    )

                    break

            else:
                # Confirmation requires consecutive closes.
                consecutive_breaks = 0

        # ---------------------------------------------------------------------
        # CONFIRMED INVERSION
        # ---------------------------------------------------------------------

        if (
            new_direction
            != fvg.direction
        ):

            fvg.inverted = True

            fvg.inversion_status = (
                InversionStatus.CONFIRMED
            )

            # The original FVG type is intentionally preserved.
            #
            # Example:
            #     original type = BULLISH
            #     active direction = BEARISH
            #
            # This allows COSMOS to understand that the object originated
            # as a bullish FVG but is now functioning as an IFVG.

            fvg.direction = new_direction

            fvg.valid = True

            fvg.evidence.extend(
                evidence
            )

            return FVGInversionResult(
                fvg=fvg,
                status=InversionStatus.CONFIRMED,
                inverted=True,
                new_direction=new_direction,
                evidence=evidence,
            )

        # ---------------------------------------------------------------------
        # POTENTIAL INVERSION
        #
        # A boundary break occurred, but confirmation requirements were not
        # satisfied.
        # ---------------------------------------------------------------------

        if potential_detected:

            fvg.inversion_status = (
                InversionStatus.POTENTIAL
            )

            potential_evidence = [
                "Potential FVG Inversion",
                (
                    f"Maximum Consecutive Breaks: "
                    f"{maximum_breaks}"
                ),
                (
                    "Waiting for close confirmation"
                ),
            ]

            fvg.evidence.extend(
                potential_evidence
            )

            return FVGInversionResult(
                fvg=fvg,
                status=InversionStatus.POTENTIAL,
                inverted=False,
                new_direction=fvg.direction,
                evidence=potential_evidence,
            )

        # ---------------------------------------------------------------------
        # NO INVERSION
        # ---------------------------------------------------------------------

        no_inversion_evidence = [
            "No Confirmed Inversion",
            "Original FVG Direction Preserved",
        ]

        return FVGInversionResult(
            fvg=fvg,
            status=InversionStatus.NONE,
            inverted=False,
            new_direction=fvg.direction,
            evidence=no_inversion_evidence,
        )

    # =========================================================================
    # CONFIRMATION
    # =========================================================================

    @staticmethod
    def _confirmation_requirement() -> int:
        """
        Return the required number of consecutive confirmation candles.

        The value is bounded by the configured maximum.
        """

        required = max(
            1,
            int(
                MIN_INVERSION_CONFIRMATION_CANDLES
            ),
        )

        return min(
            required,
            max(
                required,
                int(
                    MAX_INVERSION_CONFIRMATION_CANDLES
                ),
            ),
        )

    # =========================================================================
    # BOUNDARY
    # =========================================================================

    @staticmethod
    def _is_boundary_broken(
        fvg: FairValueGap,
        close: float,
        buffer: float,
    ) -> bool:
        """
        Determine whether a candle close has broken the FVG boundary.
        """

        if fvg.direction == FVGDirection.BULLISH:

            return (
                close
                <
                (
                    float(fvg.low)
                    - buffer
                )
            )

        if fvg.direction == FVGDirection.BEARISH:

            return (
                close
                >
                (
                    float(fvg.high)
                    + buffer
                )
            )

        return False

    # =========================================================================
    # CLOSE BUFFER
    # =========================================================================

    @staticmethod
    def _close_buffer(
        fvg: FairValueGap,
    ) -> float:
        """
        Calculate the inversion close buffer.

        The configured ratio is applied to the FVG range.
        """

        ratio = max(
            0.0,
            float(
                INVERSION_CLOSE_BUFFER_RATIO
            ),
        )

        return (
            gap_range(fvg)
            * ratio
        )

    # =========================================================================
    # EVIDENCE
    # =========================================================================

    @staticmethod
    def _confirmation_evidence(
        fvg: FairValueGap,
        confirmation_count: int,
    ) -> list[str]:
        """
        Build detailed inversion evidence.
        """

        evidence: list[str] = []

        if fvg.direction == FVGDirection.BULLISH:

            evidence.append(
                "Bullish FVG Broken"
            )

            evidence.append(
                "Close Below FVG"
            )

            evidence.append(
                "Former Support Became Resistance"
            )

        elif fvg.direction == FVGDirection.BEARISH:

            evidence.append(
                "Bearish FVG Broken"
            )

            evidence.append(
                "Close Above FVG"
            )

            evidence.append(
                "Former Resistance Became Support"
            )

        evidence.append(
            (
                f"Consecutive Confirmation Candles: "
                f"{confirmation_count}"
            )
        )

        if (
            confirmation_count
            >= STRONG_INVERSION_CONFIRMATION_CANDLES
        ):
            evidence.append(
                "Strong Inversion Confirmation"
            )

        if (
            confirmation_count
            >= INVERSION_CONFIRMATION_RATIO
        ):
            evidence.append(
                "Inversion Confirmation Threshold Met"
            )

        return evidence
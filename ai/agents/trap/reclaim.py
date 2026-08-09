"""
===============================================================================
COSMOS Trap Reclaim Engine

Detects price reclaiming a previously broken support/resistance level.

Important:
    Reclaim is evidence of breakout failure.
    It does NOT independently confirm a trap.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.trap.constants import (
    MAX_RECLAIM_BARS,
    RECLAIM_THRESHOLD,
)

from ai.agents.trap.models import (
    BreakoutEvent,
    ReclaimEvent,
    TrapDirection,
)

from ai.agents.trap.utils import (
    candle_close,
    candle_high,
    candle_low,
    candle_range,
    normalize_score,
)


class ReclaimEngine:
    """
    Detects price returning across a broken level after a breakout.

    Bullish breakout:
        Price broke ABOVE resistance.
        Reclaim occurs when price closes BACK BELOW resistance.

    Bearish breakout:
        Price broke BELOW support.
        Reclaim occurs when price closes BACK ABOVE support.
    """

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        candles,
        breakout: BreakoutEvent,
        current_index: int | None = None,
    ) -> ReclaimEvent:
        """
        Analyze candles after a breakout and determine whether the broken
        level has been reclaimed.

        The engine searches only within MAX_RECLAIM_BARS after the breakout.
        """

        if (
            breakout is None
            or
            not breakout.detected
        ):

            return ReclaimEvent()

        try:

            candle_list = list(
                candles
            )

        except TypeError:

            return ReclaimEvent()

        if not candle_list:

            return ReclaimEvent()

        breakout_index = (
            breakout.candle_index
        )

        if breakout_index < 0:

            breakout_index = (
                len(candle_list) - 1
            )

        # ---------------------------------------------------------------------
        # Determine search end.
        # ---------------------------------------------------------------------

        if current_index is None:

            current_index = (
                len(candle_list) - 1
            )

        search_start = (
            breakout_index + 1
        )

        search_end = min(
            current_index,
            breakout_index
            + MAX_RECLAIM_BARS,
        )

        if search_start > search_end:

            return ReclaimEvent()

        # ---------------------------------------------------------------------
        # Search for reclaim.
        # ---------------------------------------------------------------------

        for index in range(
            search_start,
            search_end + 1,
        ):

            candle = candle_list[
                index
            ]

            close = candle_close(
                candle
            )

            level = float(
                breakout.level
            )

            if (
                breakout.direction
                ==
                TrapDirection.BULLISH
            ):

                # -------------------------------------------------------------
                # Failed upside breakout:
                # price closes back BELOW resistance.
                # -------------------------------------------------------------

                if close < level:

                    strength = (
                        self._reclaim_strength(
                            candle,
                            level,
                            TrapDirection.BULLISH,
                        )
                    )

                    evidence = [
                        "Price reclaimed below broken resistance",
                        "Upside breakout failed to hold",
                    ]

                    bars_after_breakout = (
                        index
                        -
                        breakout_index
                    )

                    if (
                        bars_after_breakout
                        <= 1
                    ):

                        evidence.append(
                            "Reclaim occurred immediately after breakout"
                        )

                    return ReclaimEvent(

                        detected=True,

                        direction=(
                            TrapDirection.BULLISH
                        ),

                        level=level,

                        reclaim_price=close,

                        bars_after_breakout=(
                            bars_after_breakout
                        ),

                        strength=round(
                            strength,
                            2,
                        ),

                        evidence=evidence,
                    )

            elif (
                breakout.direction
                ==
                TrapDirection.BEARISH
            ):

                # -------------------------------------------------------------
                # Failed downside breakout:
                # price closes back ABOVE support.
                # -------------------------------------------------------------

                if close > level:

                    strength = (
                        self._reclaim_strength(
                            candle,
                            level,
                            TrapDirection.BEARISH,
                        )
                    )

                    evidence = [
                        "Price reclaimed above broken support",
                        "Downside breakout failed to hold",
                    ]

                    bars_after_breakout = (
                        index
                        -
                        breakout_index
                    )

                    if (
                        bars_after_breakout
                        <= 1
                    ):

                        evidence.append(
                            "Reclaim occurred immediately after breakout"
                        )

                    return ReclaimEvent(

                        detected=True,

                        direction=(
                            TrapDirection.BEARISH
                        ),

                        level=level,

                        reclaim_price=close,

                        bars_after_breakout=(
                            bars_after_breakout
                        ),

                        strength=round(
                            strength,
                            2,
                        ),

                        evidence=evidence,
                    )

        # ---------------------------------------------------------------------
        # No reclaim.
        # ---------------------------------------------------------------------

        return ReclaimEvent(
            detected=False,
            direction=(
                breakout.direction
            ),
            level=float(
                breakout.level
            ),
        )

    # =========================================================================
    # SINGLE CANDLE
    # =========================================================================

    def check_candle(
        self,
        candle,
        breakout: BreakoutEvent,
    ) -> ReclaimEvent:
        """
        Check one candle for an immediate reclaim.
        """

        if (
            breakout is None
            or
            not breakout.detected
        ):

            return ReclaimEvent()

        level = float(
            breakout.level
        )

        close = candle_close(
            candle
        )

        if (
            breakout.direction
            ==
            TrapDirection.BULLISH
            and
            close < level
        ):

            strength = (
                self._reclaim_strength(
                    candle,
                    level,
                    TrapDirection.BULLISH,
                )
            )

            return ReclaimEvent(

                detected=True,

                direction=(
                    TrapDirection.BULLISH
                ),

                level=level,

                reclaim_price=close,

                bars_after_breakout=1,

                strength=round(
                    strength,
                    2,
                ),

                evidence=[
                    "Price reclaimed below broken resistance",
                    "Immediate upside breakout failure",
                ],
            )

        if (
            breakout.direction
            ==
            TrapDirection.BEARISH
            and
            close > level
        ):

            strength = (
                self._reclaim_strength(
                    candle,
                    level,
                    TrapDirection.BEARISH,
                )
            )

            return ReclaimEvent(

                detected=True,

                direction=(
                    TrapDirection.BEARISH
                ),

                level=level,

                reclaim_price=close,

                bars_after_breakout=1,

                strength=round(
                    strength,
                    2,
                ),

                evidence=[
                    "Price reclaimed above broken support",
                    "Immediate downside breakout failure",
                ],
            )

        return ReclaimEvent(
            detected=False,
            direction=(
                breakout.direction
            ),
            level=level,
        )

    # =========================================================================
    # RECLAIM STRENGTH
    # =========================================================================

    @staticmethod
    def _reclaim_strength(
        candle,
        level: float,
        direction: TrapDirection,
    ) -> float:
        """
        Estimate reclaim strength from how decisively the candle closes
        back through the broken level.

        This is a relative evidence score, not a probability of success.
        """

        high = candle_high(
            candle
        )

        low = candle_low(
            candle
        )

        close = candle_close(
            candle
        )

        range_value = (
            candle_range(
                candle
            )
        )

        if range_value <= 0.0:

            return 0.0

        if (
            direction
            ==
            TrapDirection.BULLISH
        ):

            # For an upside breakout that failed, stronger reclaim means the
            # close is progressively deeper below resistance.

            penetration = (
                level - close
            )

            available_range = (
                max(
                    range_value,
                    abs(
                        high - level
                    ),
                    1e-12,
                )
            )

        else:

            # For a downside breakout that failed, stronger reclaim means the
            # close is progressively deeper above support.

            penetration = (
                close - level
            )

            available_range = (
                max(
                    range_value,
                    abs(
                        level - low
                    ),
                    1e-12,
                )
            )

        raw_strength = (
            penetration
            /
            available_range
        )

        return normalize_score(
            raw_strength * 100.0
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

reclaim_engine = ReclaimEngine()
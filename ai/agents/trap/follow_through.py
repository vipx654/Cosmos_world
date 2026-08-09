"""
===============================================================================
COSMOS Trap Follow-Through Engine

Measures whether a breakout receives sufficient continuation after the
initial breakout candle.

This module does NOT confirm a trap by itself.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.trap.constants import (
    MAX_RECLAIM_BARS,
    MIN_FOLLOW_THROUGH_RATIO,
    STRONG_FOLLOW_THROUGH_RATIO,
)

from ai.agents.trap.models import (
    BreakoutEvent,
    FollowThroughFailure,
    TrapDirection,
)

from ai.agents.trap.utils import (
    candle_close,
    candle_high,
    candle_low,
    normalize_score,
)


class FollowThroughEngine:
    """
    Determines whether a breakout receives meaningful continuation.

    Bullish breakout:
        Price should continue higher.

    Bearish breakout:
        Price should continue lower.

    Failure to continue increases the likelihood that the breakout was
    vulnerable to becoming a false breakout.
    """

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        candles,
        breakout: BreakoutEvent,
        current_index: int | None = None,
    ) -> FollowThroughFailure:
        """
        Analyze post-breakout price action.
        """

        if (
            breakout is None
            or
            not breakout.detected
        ):

            return FollowThroughFailure()

        try:

            candle_list = list(candles)

        except TypeError:

            return FollowThroughFailure()

        if not candle_list:

            return FollowThroughFailure()

        breakout_index = breakout.candle_index

        if breakout_index < 0:

            breakout_index = len(candle_list) - 1

        if current_index is None:

            current_index = len(candle_list) - 1

        if breakout_index >= len(candle_list):

            return FollowThroughFailure()

        # Only evaluate the immediate post-breakout window.
        search_end = min(
            current_index,
            breakout_index + MAX_RECLAIM_BARS,
        )

        if breakout_index + 1 > search_end:

            return FollowThroughFailure(
                direction=breakout.direction,
            )

        level = float(
            breakout.level
        )

        breakout_price = float(
            breakout.breakout_price
        )

        # Distance achieved by the original breakout.
        initial_extension = abs(
            breakout_price - level
        )

        if initial_extension <= 0.0:

            return FollowThroughFailure(
                direction=breakout.direction,
            )

        best_continuation = 0.0

        best_index = None

        # =====================================================================
        # Bullish breakout
        # =====================================================================

        if (
            breakout.direction
            == TrapDirection.BULLISH
        ):

            for index in range(
                breakout_index + 1,
                search_end + 1,
            ):

                candle = candle_list[index]

                continuation = max(
                    0.0,
                    candle_high(candle)
                    -
                    breakout_price,
                )

                if continuation > best_continuation:

                    best_continuation = continuation
                    best_index = index

        # =====================================================================
        # Bearish breakout
        # =====================================================================

        elif (
            breakout.direction
            == TrapDirection.BEARISH
        ):

            for index in range(
                breakout_index + 1,
                search_end + 1,
            ):

                candle = candle_list[index]

                continuation = max(
                    0.0,
                    breakout_price
                    -
                    candle_low(candle),
                )

                if continuation > best_continuation:

                    best_continuation = continuation
                    best_index = index

        else:

            return FollowThroughFailure()

        # =====================================================================
        # Continuation ratio
        # =====================================================================

        continuation_ratio = (
            best_continuation
            /
            initial_extension
        )

        continuation_ratio = max(
            0.0,
            continuation_ratio,
        )

        # =====================================================================
        # Failure detection
        # =====================================================================

        failed = (
            continuation_ratio
            <
            MIN_FOLLOW_THROUGH_RATIO
        )

        strong_failure = (
            continuation_ratio
            <
            (
                1.0
                -
                STRONG_FOLLOW_THROUGH_RATIO
            )
        )

        evidence: list[str] = []

        if failed:

            evidence.append(
                "Breakout received insufficient follow-through"
            )

        else:

            evidence.append(
                "Breakout received measurable follow-through"
            )

        if strong_failure:

            evidence.append(
                "Continuation failure was pronounced"
            )

        # =====================================================================
        # Strength
        # =====================================================================

        failure_strength = normalize_score(
            (
                1.0
                -
                min(
                    1.0,
                    continuation_ratio,
                )
            )
            * 100.0
        )

        # =====================================================================
        # Reversal confirmation
        # =====================================================================

        reversal_detected = False

        if best_index is not None:

            final_candle = candle_list[
                search_end
            ]

            final_close = candle_close(
                final_candle
            )

            if (
                breakout.direction
                == TrapDirection.BULLISH
                and
                final_close < level
            ):

                reversal_detected = True

                evidence.append(
                    "Price returned below the breakout level"
                )

            elif (
                breakout.direction
                == TrapDirection.BEARISH
                and
                final_close > level
            ):

                reversal_detected = True

                evidence.append(
                    "Price returned above the breakout level"
                )

        return FollowThroughFailure(

            detected=failed,

            direction=breakout.direction,

            continuation_ratio=round(
                continuation_ratio,
                4,
            ),

            failure_strength=round(
                failure_strength,
                2,
            ),

            reversal_detected=reversal_detected,

            bars_observed=max(
                0,
                search_end - breakout_index,
            ),

            best_continuation=round(
                best_continuation,
                10,
            ),

            evidence=evidence,
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

follow_through_engine = FollowThroughEngine()
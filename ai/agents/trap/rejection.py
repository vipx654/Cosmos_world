"""
===============================================================================
COSMOS Trap Rejection Engine

Detects rejection characteristics around a failed breakout level.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.trap.constants import (
    BULL_TRAP_CLOSE_THRESHOLD,
    BEAR_TRAP_CLOSE_THRESHOLD,
    MIN_REJECTION_WICK_RATIO,
    STRONG_REJECTION_WICK_RATIO,
)

from ai.agents.trap.models import (
    BreakoutEvent,
    ReclaimEvent,
    RejectionEvent,
    TrapDirection,
)

from ai.agents.trap.utils import (
    body_ratio,
    candle_close,
    candle_high,
    candle_low,
    candle_range,
    close_position,
    lower_wick_ratio,
    normalize_score,
    upper_wick_ratio,
)


class RejectionEngine:
    """
    Detects rejection of a breakout level.

    Bull trap:
        breakout above resistance + upper rejection.

    Bear trap:
        breakout below support + lower rejection.
    """

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        candle,
        breakout: BreakoutEvent,
        reclaim: ReclaimEvent | None = None,
    ) -> RejectionEvent:
        """
        Analyze a candle for rejection around a breakout level.
        """

        if (
            breakout is None
            or
            not breakout.detected
        ):

            return RejectionEvent()

        level = float(
            breakout.level
        )

        close_pos = close_position(
            candle
        )

        body = body_ratio(
            candle
        )

        upper_wick = upper_wick_ratio(
            candle
        )

        lower_wick = lower_wick_ratio(
            candle
        )

        evidence: list[str] = []

        # =====================================================================
        # BULL TRAP REJECTION
        # =====================================================================

        if (
            breakout.direction
            ==
            TrapDirection.BULLISH
        ):

            detected = (
                upper_wick
                >=
                MIN_REJECTION_WICK_RATIO
                and
                close_pos
                <=
                BULL_TRAP_CLOSE_THRESHOLD
            )

            # A reclaim strengthens the rejection evidence but is not required
            # for the rejection candle itself.
            if (
                reclaim is not None
                and
                reclaim.detected
            ):

                detected = True

            if detected:

                evidence.append(
                    "Upper wick shows rejection of upside breakout"
                )

                if (
                    upper_wick
                    >=
                    STRONG_REJECTION_WICK_RATIO
                ):

                    evidence.append(
                        "Strong upper rejection wick"
                    )

                if (
                    close_pos
                    <=
                    BULL_TRAP_CLOSE_THRESHOLD
                ):

                    evidence.append(
                        "Close returned toward lower portion of candle"
                    )

                strength = (
                    self._strength(
                        wick_ratio=upper_wick,
                        close_position=close_pos,
                        body_ratio_value=body,
                        direction=(
                            TrapDirection.BULLISH
                        ),
                    )
                )

                return RejectionEvent(

                    detected=True,

                    direction=(
                        TrapDirection.BULLISH
                    ),

                    wick_ratio=upper_wick,

                    body_ratio=body,

                    close_position=close_pos,

                    strength=round(
                        strength,
                        2,
                    ),

                    candle_index=(
                        breakout.candle_index
                    ),

                    evidence=evidence,
                )

            return RejectionEvent(
                detected=False,
                direction=(
                    TrapDirection.BULLISH
                ),
                wick_ratio=upper_wick,
                body_ratio=body,
                close_position=close_pos,
                candle_index=(
                    breakout.candle_index
                ),
            )

        # =====================================================================
        # BEAR TRAP REJECTION
        # =====================================================================

        if (
            breakout.direction
            ==
            TrapDirection.BEARISH
        ):

            detected = (
                lower_wick
                >=
                MIN_REJECTION_WICK_RATIO
                and
                close_pos
                >=
                BEAR_TRAP_CLOSE_THRESHOLD
            )

            if (
                reclaim is not None
                and
                reclaim.detected
            ):

                detected = True

            if detected:

                evidence.append(
                    "Lower wick shows rejection of downside breakout"
                )

                if (
                    lower_wick
                    >=
                    STRONG_REJECTION_WICK_RATIO
                ):

                    evidence.append(
                        "Strong lower rejection wick"
                    )

                if (
                    close_pos
                    >=
                    BEAR_TRAP_CLOSE_THRESHOLD
                ):

                    evidence.append(
                        "Close returned toward upper portion of candle"
                    )

                strength = (
                    self._strength(
                        wick_ratio=lower_wick,
                        close_position=close_pos,
                        body_ratio_value=body,
                        direction=(
                            TrapDirection.BEARISH
                        ),
                    )
                )

                return RejectionEvent(

                    detected=True,

                    direction=(
                        TrapDirection.BEARISH
                    ),

                    wick_ratio=lower_wick,

                    body_ratio=body,

                    close_position=close_pos,

                    strength=round(
                        strength,
                        2,
                    ),

                    candle_index=(
                        breakout.candle_index
                    ),

                    evidence=evidence,
                )

            return RejectionEvent(
                detected=False,
                direction=(
                    TrapDirection.BEARISH
                ),
                wick_ratio=lower_wick,
                body_ratio=body,
                close_position=close_pos,
                candle_index=(
                    breakout.candle_index
                ),
            )

        return RejectionEvent()

    # =========================================================================
    # LEVEL-SPECIFIC ANALYSIS
    # =========================================================================

    def analyze_at_level(
        self,
        candle,
        level: float,
        direction: TrapDirection,
        candle_index: int = -1,
    ) -> RejectionEvent:
        """
        Analyze rejection around an explicit level.
        """

        if direction == TrapDirection.BULLISH:

            breakout = BreakoutEvent(
                detected=True,
                direction=(
                    TrapDirection.BULLISH
                ),
                level=float(level),
                breakout_price=candle_high(
                    candle
                ),
                candle_index=candle_index,
            )

        elif direction == TrapDirection.BEARISH:

            breakout = BreakoutEvent(
                detected=True,
                direction=(
                    TrapDirection.BEARISH
                ),
                level=float(level),
                breakout_price=candle_low(
                    candle
                ),
                candle_index=candle_index,
            )

        else:

            return RejectionEvent()

        return self.analyze(
            candle,
            breakout,
        )

    # =========================================================================
    # STRENGTH
    # =========================================================================

    @staticmethod
    def _strength(
        wick_ratio: float,
        close_position: float,
        body_ratio_value: float,
        direction: TrapDirection,
    ) -> float:
        """
        Calculate rejection strength.

        Stronger rejection is associated with:

            - larger rejection wick
            - close away from breakout extreme
            - meaningful candle body

        This is an evidence score, not a trade-success probability.
        """

        wick_score = normalize_score(
            wick_ratio * 100.0
        )

        if (
            direction
            ==
            TrapDirection.BULLISH
        ):

            close_score = (
                1.0
                -
                close_position
            ) * 100.0

        elif (
            direction
            ==
            TrapDirection.BEARISH
        ):

            close_score = (
                close_position
                *
                100.0
            )

        else:

            close_score = 0.0

        close_score = normalize_score(
            close_score
        )

        body_score = normalize_score(
            body_ratio_value
            * 100.0
        )

        # Wick receives the greatest weight because rejection is the primary
        # feature being measured.
        strength = (
            wick_score * 0.55
            +
            close_score * 0.35
            +
            body_score * 0.10
        )

        return normalize_score(
            strength
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

rejection_engine = RejectionEngine()
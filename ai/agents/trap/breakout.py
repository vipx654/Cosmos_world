"""
===============================================================================
COSMOS Trap Breakout Detector

Detects meaningful price extensions beyond support/resistance levels.

Important:
    This module detects BREAKOUT EVENTS only.
    It does not declare a trap.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.trap.constants import (
    DEFAULT_LOOKBACK,
    MIN_BREAK_DISTANCE_RATIO,
    MIN_EXTENSION_RATIO,
)

from ai.agents.trap.models import (
    BreakoutEvent,
    TrapDirection,
)

from ai.agents.trap.utils import (
    candle_close,
    candle_high,
    candle_low,
    candle_range,
    extension_above_level,
    extension_below_level,
    extension_ratio,
)


# =============================================================================
# ENGINE
# =============================================================================


class BreakoutEngine:
    """
    Detects bullish and bearish breakout events.

    Bullish breakout:
        price trades above resistance.

    Bearish breakout:
        price trades below support.

    A breakout is only an initial event. Reclaim/rejection/follow-through
    analysis is required before it can become a trap.
    """

    # =========================================================================
    # BULLISH BREAKOUT
    # =========================================================================

    def detect_above(
        self,
        candle,
        resistance: float,
        candle_index: int = -1,
    ) -> BreakoutEvent:
        """
        Detect price breaking above resistance.
        """

        high = candle_high(
            candle
        )

        close = candle_close(
            candle
        )

        level = float(
            resistance
        )

        extension = (
            extension_above_level(
                high,
                level,
            )
        )

        range_value = candle_range(
            candle
        )

        ratio = extension_ratio(
            extension,
            range_value,
        )

        detected = (
            extension > 0.0
            and
            ratio >= MIN_BREAK_DISTANCE_RATIO
        )

        evidence: list[str] = []

        if detected:

            evidence.append(
                "Price traded above resistance"
            )

            evidence.append(
                "Breakout extension exceeded minimum threshold"
            )

            if close > level:

                evidence.append(
                    "Candle closed above resistance"
                )

            else:

                evidence.append(
                    "Candle failed to close above resistance"
                )

        return BreakoutEvent(

            detected=detected,

            direction=(
                TrapDirection.BULLISH
                if detected
                else TrapDirection.NEUTRAL
            ),

            level=level,

            breakout_price=high,

            extension=extension,

            extension_ratio=ratio,

            candle_index=candle_index,

            evidence=evidence,
        )

    # =========================================================================
    # BEARISH BREAKOUT
    # =========================================================================

    def detect_below(
        self,
        candle,
        support: float,
        candle_index: int = -1,
    ) -> BreakoutEvent:
        """
        Detect price breaking below support.
        """

        low = candle_low(
            candle
        )

        close = candle_close(
            candle
        )

        level = float(
            support
        )

        extension = (
            extension_below_level(
                low,
                level,
            )
        )

        range_value = candle_range(
            candle
        )

        ratio = extension_ratio(
            extension,
            range_value,
        )

        detected = (
            extension > 0.0
            and
            ratio >= MIN_BREAK_DISTANCE_RATIO
        )

        evidence: list[str] = []

        if detected:

            evidence.append(
                "Price traded below support"
            )

            evidence.append(
                "Breakout extension exceeded minimum threshold"
            )

            if close < level:

                evidence.append(
                    "Candle closed below support"
                )

            else:

                evidence.append(
                    "Candle failed to close below support"
                )

        return BreakoutEvent(

            detected=detected,

            direction=(
                TrapDirection.BEARISH
                if detected
                else TrapDirection.NEUTRAL
            ),

            level=level,

            breakout_price=low,

            extension=extension,

            extension_ratio=ratio,

            candle_index=candle_index,

            evidence=evidence,
        )

    # =========================================================================
    # AUTOMATIC LEVEL DETECTION
    # =========================================================================

    def detect(
        self,
        candles,
        resistance: float | None = None,
        support: float | None = None,
        lookback: int = DEFAULT_LOOKBACK,
    ) -> list[BreakoutEvent]:
        """
        Detect breakout events from a candle sequence.

        Explicit resistance/support levels are preferred.

        If levels are not supplied, the engine derives simple reference
        levels from the preceding lookback candles.

        The current candle is excluded from automatic level construction.
        """

        try:

            candle_list = list(
                candles
            )

        except TypeError:

            return []

        if len(
            candle_list
        ) < 2:

            return []

        lookback = max(
            1,
            int(
                lookback
            ),
        )

        current_index = (
            len(candle_list) - 1
        )

        current_candle = (
            candle_list[-1]
        )

        previous = candle_list[
            max(
                0,
                len(candle_list)
                - 1
                - lookback,
            ):
            -1
        ]

        # ---------------------------------------------------------------------
        # Automatically derive levels if necessary.
        # ---------------------------------------------------------------------

        if resistance is None:

            resistance = self._highest_high(
                previous
            )

        if support is None:

            support = self._lowest_low(
                previous
            )

        events: list[BreakoutEvent] = []

        # ---------------------------------------------------------------------
        # Bullish breakout
        # ---------------------------------------------------------------------

        bullish = self.detect_above(
            current_candle,
            resistance,
            current_index,
        )

        if bullish.detected:

            events.append(
                bullish
            )

        # ---------------------------------------------------------------------
        # Bearish breakout
        # ---------------------------------------------------------------------

        bearish = self.detect_below(
            current_candle,
            support,
            current_index,
        )

        if bearish.detected:

            events.append(
                bearish
            )

        return events

    # =========================================================================
    # RANGE LEVELS
    # =========================================================================

    @staticmethod
    def _highest_high(
        candles,
    ) -> float:

        values = [
            candle_high(
                candle
            )
            for candle in candles
        ]

        if not values:

            return 0.0

        return max(
            values
        )

    @staticmethod
    def _lowest_low(
        candles,
    ) -> float:

        values = [
            candle_low(
                candle
            )
            for candle in candles
        ]

        if not values:

            return 0.0

        return min(
            values
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

breakout_engine = BreakoutEngine()
"""
===============================================================================
COSMOS Swing Engine

Detects Swing Highs and Swing Lows.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.models import MarketCandle
from ai.models import SwingPoint
from ai.models import SwingType


class SwingEngine:
    """
    Detect swing highs and swing lows.
    """

    def __init__(
        self,
        lookback: int = 3,
    ):
        self.lookback = lookback

    def detect(
        self,
        candles: list[MarketCandle],
    ) -> list[SwingPoint]:

        swings: list[SwingPoint] = []

        if len(candles) < (self.lookback * 2 + 1):
            return swings

        for index in range(
            self.lookback,
            len(candles) - self.lookback,
        ):

            current = candles[index]

            # -----------------------------------------------------
            # Swing High
            # -----------------------------------------------------

            is_high = True

            for i in range(
                index - self.lookback,
                index + self.lookback + 1,
            ):

                if i == index:
                    continue

                if candles[i].high >= current.high:
                    is_high = False
                    break

            if is_high:

                swings.append(
                    SwingPoint(
                        index=index,
                        price=current.high,
                        timestamp=current.timestamp,
                        swing_type=SwingType.HIGH,
                    )
                )

            # -----------------------------------------------------
            # Swing Low
            # -----------------------------------------------------

            is_low = True

            for i in range(
                index - self.lookback,
                index + self.lookback + 1,
            ):

                if i == index:
                    continue

                if candles[i].low <= current.low:
                    is_low = False
                    break

            if is_low:

                swings.append(
                    SwingPoint(
                        index=index,
                        price=current.low,
                        timestamp=current.timestamp,
                        swing_type=SwingType.LOW,
                    )
                )

        swings.sort(
            key=lambda x: x.index,
        )

        return swings
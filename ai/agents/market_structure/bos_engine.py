"""
===============================================================================
COSMOS BOS Engine

Break Of Structure Detection

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import SwingPoint
from ai.models import SwingType


@dataclass(slots=True)
class BOSAnalysis:
    """
    Break Of Structure result.
    """

    bullish: bool

    bearish: bool

    broken_price: float | None

    confidence: float


class BOSEngine:
    """
    Detects institutional Break Of Structure.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> BOSAnalysis:

        if len(swings) < 4:

            return BOSAnalysis(
                bullish=False,
                bearish=False,
                broken_price=None,
                confidence=0.0,
            )

        highs = [
            s for s in swings
            if s.swing_type == SwingType.HIGH
        ]

        lows = [
            s for s in swings
            if s.swing_type == SwingType.LOW
        ]

        bullish = False
        bearish = False

        broken_price = None

        confidence = 0.0

        # ---------------------------------------------------------
        # Bullish BOS
        # ---------------------------------------------------------

        if len(highs) >= 2:

            previous = highs[-2]

            current = highs[-1]

            if current.price > previous.price:

                bullish = True

                broken_price = previous.price

                confidence = 85.0

        # ---------------------------------------------------------
        # Bearish BOS
        # ---------------------------------------------------------

        if len(lows) >= 2:

            previous = lows[-2]

            current = lows[-1]

            if current.price < previous.price:

                bearish = True

                broken_price = previous.price

                confidence = max(
                    confidence,
                    85.0,
                )

        return BOSAnalysis(

            bullish=bullish,

            bearish=bearish,

            broken_price=broken_price,

            confidence=confidence,
        )
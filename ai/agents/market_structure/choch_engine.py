"""
===============================================================================
COSMOS CHOCH Engine

Change Of Character Detection

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import SwingPoint
from ai.models import SwingType


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class CHOCHAnalysis:
    """
    Change Of Character result.
    """

    detected: bool

    bullish: bool

    bearish: bool

    confidence: float


# =============================================================================
# ENGINE
# =============================================================================


class CHOCHEngine:
    """
    Detects Change Of Character.

    CHOCH represents the first structural warning
    that the current trend may be changing.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> CHOCHAnalysis:

        if len(swings) < 6:

            return CHOCHAnalysis(
                detected=False,
                bullish=False,
                bearish=False,
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

        # ---------------------------------------------------------
        # Bullish CHOCH
        # Lower High broken
        # ---------------------------------------------------------

        if len(highs) >= 2:

            if highs[-1].price > highs[-2].price:

                bullish = True

        # ---------------------------------------------------------
        # Bearish CHOCH
        # Higher Low broken
        # ---------------------------------------------------------

        if len(lows) >= 2:

            if lows[-1].price < lows[-2].price:

                bearish = True

        detected = bullish or bearish

        confidence = 0.0

        if detected:

            confidence = 75.0

        return CHOCHAnalysis(

            detected=detected,

            bullish=bullish,

            bearish=bearish,

            confidence=confidence,
        )
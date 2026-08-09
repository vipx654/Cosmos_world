"""
===============================================================================
COSMOS Trendline Engine

Institutional trendline detection.

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
class TrendlineAnalysis:
    """
    Trendline confirmation.
    """

    bullish_trendline: bool

    bearish_trendline: bool

    slope: float

    touches: int

    confidence: float


# =============================================================================
# ENGINE
# =============================================================================


class TrendlineEngine:
    """
    Builds trendlines from confirmed swing points.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> TrendlineAnalysis:

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

        slope = 0.0
        touches = 0
        confidence = 0.0

        # ---------------------------------------------------------
        # Bullish Trendline
        # ---------------------------------------------------------

        if len(lows) >= 2:

            p1 = lows[-2]
            p2 = lows[-1]

            dx = p2.index - p1.index

            if dx != 0:

                slope = (p2.price - p1.price) / dx

                if slope > 0:
                    bullish = True
                    touches = len(lows)
                    confidence = min(
                        100.0,
                        50.0 + touches * 10,
                    )

        # ---------------------------------------------------------
        # Bearish Trendline
        # ---------------------------------------------------------

        if len(highs) >= 2:

            p1 = highs[-2]
            p2 = highs[-1]

            dx = p2.index - p1.index

            if dx != 0:

                down_slope = (p2.price - p1.price) / dx

                if down_slope < 0:

                    bearish = True

                    if abs(down_slope) > abs(slope):
                        slope = down_slope

                    touches = max(
                        touches,
                        len(highs),
                    )

                    confidence = max(
                        confidence,
                        min(
                            100.0,
                            50.0 + len(highs) * 10,
                        ),
                    )

        return TrendlineAnalysis(
            bullish_trendline=bullish,
            bearish_trendline=bearish,
            slope=slope,
            touches=touches,
            confidence=confidence,
        )
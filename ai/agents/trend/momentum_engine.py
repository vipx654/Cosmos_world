"""
===============================================================================
COSMOS Momentum Engine

Measures market momentum and trend strength.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import MarketCandle


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class MomentumAnalysis:
    """
    Market momentum analysis.
    """

    velocity: float

    acceleration: float

    bullish: bool

    bearish: bool

    confidence: float


# =============================================================================
# ENGINE
# =============================================================================


class MomentumEngine:
    """
    Measures price momentum.

    This engine is NOT an oscillator.
    It evaluates how aggressively price is moving.
    """

    def analyze(
        self,
        candles: list[MarketCandle],
    ) -> MomentumAnalysis:

        if len(candles) < 10:
            return MomentumAnalysis(
                velocity=0.0,
                acceleration=0.0,
                bullish=False,
                bearish=False,
                confidence=0.0,
            )

        closes = [c.close for c in candles]

        # ---------------------------------------------------------
        # Velocity
        # ---------------------------------------------------------

        velocity = closes[-1] - closes[-6]

        # ---------------------------------------------------------
        # Acceleration
        # ---------------------------------------------------------

        previous_velocity = closes[-6] - closes[-10]

        acceleration = velocity - previous_velocity

        bullish = velocity > 0

        bearish = velocity < 0

        confidence = abs(velocity) * 10

        if abs(acceleration) > abs(velocity * 0.25):
            confidence += 15

        confidence = max(0.0, min(confidence, 100.0))

        return MomentumAnalysis(
            velocity=velocity,
            acceleration=acceleration,
            bullish=bullish,
            bearish=bearish,
            confidence=confidence,
        )
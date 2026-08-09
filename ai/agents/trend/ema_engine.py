"""
===============================================================================
COSMOS EMA Engine

Institutional EMA confirmation engine.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import MarketCandle


# =============================================================================
# MODELS
# =============================================================================


@dataclass(slots=True)
class EMAAnalysis:
    """
    EMA confirmation analysis.
    """

    ema20: float
    ema50: float
    ema100: float
    ema200: float

    bullish_alignment: bool
    bearish_alignment: bool

    compression: bool
    expansion: bool

    slope: float

    confidence: float


# =============================================================================
# ENGINE
# =============================================================================


class EMAEngine:
    """
    EMA confirmation engine.

    EMA is used only for trend confirmation,
    never as a standalone signal.
    """

    @staticmethod
    def calculate(
        prices: list[float],
        period: int,
    ) -> float:

        if len(prices) < period:
            return prices[-1]

        multiplier = 2 / (period + 1)

        ema = sum(prices[:period]) / period

        for price in prices[period:]:

            ema = (price - ema) * multiplier + ema

        return ema

    def analyze(
        self,
        candles: list[MarketCandle],
    ) -> EMAAnalysis:

        closes = [c.close for c in candles]

        ema20 = self.calculate(closes, 20)
        ema50 = self.calculate(closes, 50)
        ema100 = self.calculate(closes, 100)
        ema200 = self.calculate(closes, 200)

        bullish = (
            ema20 > ema50 > ema100 > ema200
        )

        bearish = (
            ema20 < ema50 < ema100 < ema200
        )

        compression = abs(ema20 - ema50) < (ema20 * 0.001)

        expansion = abs(ema20 - ema50) > (ema20 * 0.005)

        slope = ema20 - ema50

        confidence = 50.0

        if bullish:
            confidence += 20

        if bearish:
            confidence += 20

        if expansion:
            confidence += 15

        if compression:
            confidence -= 10

        confidence = max(0.0, min(confidence, 100.0))

        return EMAAnalysis(
            ema20=ema20,
            ema50=ema50,
            ema100=ema100,
            ema200=ema200,
            bullish_alignment=bullish,
            bearish_alignment=bearish,
            compression=compression,
            expansion=expansion,
            slope=slope,
            confidence=confidence,
        )
"""
===============================================================================
COSMOS Trend Confidence Engine

Combines every Trend sub-engine into one institutional confidence score.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.trend.ema_engine import EMAAnalysis
from ai.agents.trend.momentum_engine import MomentumAnalysis
from ai.agents.trend.trendline_engine import TrendlineAnalysis


class ConfidenceEngine:
    """
    Combines multiple analysis engines into one confidence score.
    """

    def calculate(
        self,
        ema: EMAAnalysis,
        momentum: MomentumAnalysis,
        trendline: TrendlineAnalysis,
    ) -> float:

        score = 0.0

        # ---------------------------------------------------------
        # EMA (40%)
        # ---------------------------------------------------------

        score += ema.confidence * 0.40

        # ---------------------------------------------------------
        # Momentum (35%)
        # ---------------------------------------------------------

        score += momentum.confidence * 0.35

        # ---------------------------------------------------------
        # Trendline (25%)
        # ---------------------------------------------------------

        score += trendline.confidence * 0.25

        return round(
            min(score, 100.0),
            2,
        )
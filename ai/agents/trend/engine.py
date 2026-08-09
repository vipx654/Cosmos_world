"""
===============================================================================
COSMOS Trend Engine

Main orchestrator for institutional trend analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.context import MarketContext
from ai.models import AgentResult
from ai.models import TrendAnalysis
from ai.models import TrendDirection

from ai.agents.trend.swing_engine import SwingEngine
from ai.agents.trend.dow_engine import DowEngine
from ai.agents.trend.ema_engine import EMAEngine
from ai.agents.trend.momentum_engine import MomentumEngine
from ai.agents.trend.trendline_engine import TrendlineEngine
from ai.agents.trend.confidence_engine import ConfidenceEngine

from ai.agents.trend.validator import TrendValidator
from ai.agents.trend.models import StructureType


class TrendEngine:
    """
    Institutional Trend Engine.

    This engine coordinates all Trend sub-engines.

    It never performs heavy calculations itself.
    """

    def __init__(self):

        self.swing_engine = SwingEngine()

        self.dow_engine = DowEngine()

        self.ema_engine = EMAEngine()

        self.momentum_engine = MomentumEngine()

        self.trendline_engine = TrendlineEngine()

        self.confidence_engine = ConfidenceEngine()

    def analyze(
        self,
        context: MarketContext,
    ) -> AgentResult:

        TrendValidator.validate(context)

        # ---------------------------------------------------------
        # Swing Detection
        # ---------------------------------------------------------

        swings = self.swing_engine.detect(
            context.candles,
        )

        # ---------------------------------------------------------
        # Dow Theory
        # ---------------------------------------------------------

        structures = self.dow_engine.analyze(
            swings,
        )

        # ---------------------------------------------------------
        # EMA
        # ---------------------------------------------------------

        ema = self.ema_engine.analyze(
            context.candles,
        )

        # ---------------------------------------------------------
        # Momentum
        # ---------------------------------------------------------

        momentum = self.momentum_engine.analyze(
            context.candles,
        )

        # ---------------------------------------------------------
        # Trendline
        # ---------------------------------------------------------

        trendline = self.trendline_engine.analyze(
            swings,
        )

        # ---------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------

        confidence = self.confidence_engine.calculate(
            ema=ema,
            momentum=momentum,
            trendline=trendline,
        )

        # ---------------------------------------------------------
        # Direction
        # ---------------------------------------------------------

        direction = TrendDirection.SIDEWAYS

        if len(structures) >= 2:

            last = structures[-2:]

            if (
                last[0] == StructureType.HH
                and
                last[1] == StructureType.HL
            ):
                direction = TrendDirection.BULLISH

            elif (
                last[0] == StructureType.LH
                and
                last[1] == StructureType.LL
            ):
                direction = TrendDirection.BEARISH

        # ---------------------------------------------------------
        # Final Analysis
        # ---------------------------------------------------------

        analysis = TrendAnalysis(

            direction=direction,

            confidence=confidence,

            strength=momentum.confidence,

            structure=" → ".join(
            s.value for s in structures[-6:]
            ),

            structures=[
            s.value
            for s in structures
            ],

            acceleration=(
                momentum.acceleration > 0
            ),

            momentum=momentum.velocity,

            reasons=[

                f"EMA Confidence: {ema.confidence:.2f}",

                f"Momentum Confidence: {momentum.confidence:.2f}",

                f"Trendline Confidence: {trendline.confidence:.2f}",

            ],
        )

        result = AgentResult(

            name="trend",

            confidence=confidence,

            success=True,

            analysis=analysis,

        )

        context.add_result(result)

        return result
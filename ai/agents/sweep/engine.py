"""
===============================================================================
COSMOS Sweep Engine

Main orchestrator for institutional liquidity sweep analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.context import MarketContext
from ai.models import AgentResult

from ai.agents.sweep.models import (
    SweepAnalysis,
    SweepDirection,
)

from ai.agents.sweep.validator import SweepValidator

from ai.agents.sweep.buy_side_sweep import (
    BuySideSweepEngine,
)

from ai.agents.sweep.sell_side_sweep import (
    SellSideSweepEngine,
)

from ai.agents.sweep.fake_sweep import (
    FakeSweepEngine,
)

from ai.agents.sweep.session_sweep import (
    SessionSweepEngine,
)

from ai.agents.sweep.confirmation_engine import (
    ConfirmationEngine,
)

from ai.agents.sweep.probability_engine import (
    ProbabilityEngine,
)

from ai.agents.sweep.confidence_engine import (
    ConfidenceEngine,
)

from ai.agents.sweep.sweep_map import (
    SweepMapEngine,
)


class SweepEngine:
    """
    Main Sweep Agent orchestrator.

    Coordinates all Sweep sub-engines.

    V1 responsibilities:

    - Validate market context
    - Read liquidity information
    - Detect buy-side sweeps
    - Detect sell-side sweeps
    - Detect possible fake sweeps
    - Tag trading sessions
    - Confirm sweeps
    - Calculate probability
    - Calculate confidence
    - Build sweep map
    - Publish AgentResult
    """

    AGENT_NAME = "sweep"

    AGENT_VERSION = "1.0.0"

    def __init__(self) -> None:

        self.buy_side_engine = (
            BuySideSweepEngine()
        )

        self.sell_side_engine = (
            SellSideSweepEngine()
        )

        self.fake_sweep_engine = (
            FakeSweepEngine()
        )

        self.session_engine = (
            SessionSweepEngine()
        )

        self.confirmation_engine = (
            ConfirmationEngine()
        )

        self.probability_engine = (
            ProbabilityEngine()
        )

        self.confidence_engine = (
            ConfidenceEngine()
        )

        self.map_engine = (
            SweepMapEngine()
        )

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        context: MarketContext,
    ) -> AgentResult:

        # ---------------------------------------------------------------------
        # Validation
        # ---------------------------------------------------------------------

        SweepValidator.validate(
            context
        )

        # ---------------------------------------------------------------------
        # Retrieve Liquidity Data
        # ---------------------------------------------------------------------

        liquidity_memory = context.memory.get(
            "liquidity"
        )

        if liquidity_memory is None:

            raise RuntimeError(
                "Liquidity Agent result is required "
                "before Sweep Agent execution."
            )

        # ---------------------------------------------------------------------
        # Retrieve Liquidity Levels
        # ---------------------------------------------------------------------

        buy_side_levels = (
            liquidity_memory.get(
                "buy_side",
                [],
            )
        )

        sell_side_levels = (
            liquidity_memory.get(
                "sell_side",
                [],
            )
        )

        liquidity_levels = (
            buy_side_levels
            +
            sell_side_levels
        )

        # ---------------------------------------------------------------------
        # Buy Side Sweep
        # ---------------------------------------------------------------------

        buy_side = (
            self.buy_side_engine.analyze(
                context.candles,
                liquidity_levels,
            )
        )

        # ---------------------------------------------------------------------
        # Sell Side Sweep
        # ---------------------------------------------------------------------

        sell_side = (
            self.sell_side_engine.analyze(
                context.candles,
                liquidity_levels,
            )
        )

        # ---------------------------------------------------------------------
        # Combine Raw Sweeps
        # ---------------------------------------------------------------------

        all_sweeps = (
            buy_side
            +
            sell_side
        )

        # ---------------------------------------------------------------------
        # Probability
        # ---------------------------------------------------------------------

        all_sweeps = (
            self.probability_engine.calculate(
                all_sweeps,
            )
        )

        # ---------------------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------------------

        overall_confidence = (
            self.confidence_engine.calculate(
                all_sweeps,
            )
        )

        # ---------------------------------------------------------------------
        # Fake Sweep Detection
        # ---------------------------------------------------------------------

        fake_sweeps = (
            self.fake_sweep_engine.analyze(
                all_sweeps,
            )
        )

        # ---------------------------------------------------------------------
        # Session Classification
        # ---------------------------------------------------------------------

        all_sweeps = (
            self.session_engine.analyze(
                all_sweeps,
                context.candles,
            )
        )

        # ---------------------------------------------------------------------
        # Confirmation
        # ---------------------------------------------------------------------

        confirmed = (
            self.confirmation_engine.analyze(
                all_sweeps,
            )
        )

        # ---------------------------------------------------------------------
        # Build Sweep Map
        # ---------------------------------------------------------------------

        sweep_map = (
            self.map_engine.build(
                buy_side=buy_side,
                sell_side=sell_side,
                fake_sweeps=fake_sweeps,
                confirmed=confirmed,
            )
        )

        # ---------------------------------------------------------------------
        # Determine Direction
        # ---------------------------------------------------------------------

        direction = (
            self._determine_direction(
                confirmed,
            )
        )

        # ---------------------------------------------------------------------
        # Overall Probability
        # ---------------------------------------------------------------------

        probability = (
            self._calculate_overall_probability(
                all_sweeps,
            )
        )

        # ---------------------------------------------------------------------
        # Reasons
        # ---------------------------------------------------------------------

        reasons = (
            self._build_reasons(
                buy_side=buy_side,
                sell_side=sell_side,
                fake_sweeps=fake_sweeps,
                confirmed=confirmed,
                probability=probability,
                confidence=overall_confidence,
            )
        )

        # ---------------------------------------------------------------------
        # Final Analysis
        # ---------------------------------------------------------------------

        analysis = SweepAnalysis(
            direction=direction,
            confidence=overall_confidence,
            probability=probability,
            sweep_map=sweep_map,
            reasons=reasons,
        )

        # ---------------------------------------------------------------------
        # Agent Result
        # ---------------------------------------------------------------------

        result = AgentResult(
            name=self.AGENT_NAME,
            confidence=overall_confidence,
            success=True,
            analysis=analysis,
        )

        # ---------------------------------------------------------------------
        # Shared Memory
        # ---------------------------------------------------------------------

        context.memory["sweep"] = {
            "analysis": analysis,
            "buy_side": buy_side,
            "sell_side": sell_side,
            "fake_sweeps": fake_sweeps,
            "confirmed": confirmed,
            "probability": probability,
            "confidence": overall_confidence,
        }

        # ---------------------------------------------------------------------
        # Store Result
        # ---------------------------------------------------------------------

        context.add_result(
            result
        )

        return result

    # =========================================================================
    # DIRECTION
    # =========================================================================

    @staticmethod
    def _determine_direction(
        sweeps,
    ) -> SweepDirection:

        if not sweeps:
            return SweepDirection.NEUTRAL

        bullish = 0
        bearish = 0

        for sweep in sweeps:

            if sweep.direction == (
                SweepDirection.BULLISH
            ):

                bullish += 1

            elif sweep.direction == (
                SweepDirection.BEARISH
            ):

                bearish += 1

        if bullish > bearish:
            return SweepDirection.BULLISH

        if bearish > bullish:
            return SweepDirection.BEARISH

        return SweepDirection.NEUTRAL

    # =========================================================================
    # PROBABILITY
    # =========================================================================

    @staticmethod
    def _calculate_overall_probability(
        sweeps,
    ) -> float:

        if not sweeps:
            return 0.0

        total = sum(
            sweep.probability
            for sweep in sweeps
        )

        return round(
            total / len(sweeps),
            2,
        )

    # =========================================================================
    # REASONS
    # =========================================================================

    @staticmethod
    def _build_reasons(
        buy_side,
        sell_side,
        fake_sweeps,
        confirmed,
        probability,
        confidence,
    ) -> list[str]:

        reasons = [
            (
                f"Buy Side Sweeps: "
                f"{len(buy_side)}"
            ),
            (
                f"Sell Side Sweeps: "
                f"{len(sell_side)}"
            ),
            (
                f"Confirmed Sweeps: "
                f"{len(confirmed)}"
            ),
            (
                f"Possible Fake Sweeps: "
                f"{len(fake_sweeps)}"
            ),
            (
                f"Average Probability: "
                f"{probability:.2f}"
            ),
            (
                f"Overall Confidence: "
                f"{confidence:.2f}"
            ),
        ]

        return reasons
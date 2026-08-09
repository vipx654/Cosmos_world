"""
===============================================================================
COSMOS Order Block Engine

Main orchestrator for institutional Order Block analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.context import MarketContext
from ai.models import AgentResult

from ai.agents.order_block.models import (
    OrderBlock,
    OrderBlockAnalysis,
    OrderBlockDirection,
)

from ai.agents.order_block.validator import (
    OrderBlockValidator,
)

from ai.agents.order_block.bullish_order_block import (
    BullishOrderBlockEngine,
)

from ai.agents.order_block.bearish_order_block import (
    BearishOrderBlockEngine,
)

from ai.agents.order_block.mitigation_engine import (
    MitigationEngine,
)

from ai.agents.order_block.breaker_engine import (
    BreakerEngine,
)

from ai.agents.order_block.confirmation_engine import (
    ConfirmationEngine,
)

from ai.agents.order_block.probability_engine import (
    ProbabilityEngine,
)

from ai.agents.order_block.confidence_engine import (
    ConfidenceEngine,
)

from ai.agents.order_block.order_block_map import (
    OrderBlockMapEngine,
)

from ai.agents.order_block.utils import (
    strongest_order_block,
)


class OrderBlockEngine:
    """
    Main Order Block Agent orchestrator.

    Pipeline
    --------
    1. Validate context
    2. Detect bullish order blocks
    3. Detect bearish order blocks
    4. Calculate probability
    5. Analyze mitigation
    6. Detect breakers
    7. Confirm blocks
    8. Calculate final confidence
    9. Build order-block map
    10. Build final analysis
    11. Store result in shared context
    """

    AGENT_NAME = "order_block"

    AGENT_VERSION = "1.0.0"

    def __init__(self) -> None:

        self.bullish_engine = (
            BullishOrderBlockEngine()
        )

        self.bearish_engine = (
            BearishOrderBlockEngine()
        )

        self.mitigation_engine = (
            MitigationEngine()
        )

        self.breaker_engine = (
            BreakerEngine()
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
            OrderBlockMapEngine()
        )

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        context: MarketContext,
    ) -> AgentResult:

        # ---------------------------------------------------------------------
        # 1. Validate context
        # ---------------------------------------------------------------------

        OrderBlockValidator.validate(
            context
        )

        candles = context.candles

        # ---------------------------------------------------------------------
        # 2. Detect bullish order blocks
        # ---------------------------------------------------------------------

        bullish_blocks = (
            self.bullish_engine.analyze(
                candles
            )
        )

        # ---------------------------------------------------------------------
        # 3. Detect bearish order blocks
        # ---------------------------------------------------------------------

        bearish_blocks = (
            self.bearish_engine.analyze(
                candles
            )
        )

        blocks: list[OrderBlock] = (
            bullish_blocks
            +
            bearish_blocks
        )

        # ---------------------------------------------------------------------
        # No blocks detected
        # ---------------------------------------------------------------------

        if not blocks:

            analysis = (
                self._empty_analysis()
            )

            result = AgentResult(
                name=self.AGENT_NAME,
                confidence=0.0,
                success=True,
                analysis=analysis,
            )

            self._store_result(
                context,
                result,
            )

            return result

        # ---------------------------------------------------------------------
        # 4. Probability
        # ---------------------------------------------------------------------

        blocks = (
            self.probability_engine.calculate(
                blocks
            )
        )

        # ---------------------------------------------------------------------
        # 5. Mitigation
        # ---------------------------------------------------------------------

        self.mitigation_engine.analyze(
            blocks,
            candles,
        )

        # ---------------------------------------------------------------------
        # 6. Breakers
        # ---------------------------------------------------------------------

        breakers = (
            self.breaker_engine.analyze(
                blocks
            )
        )

        # ---------------------------------------------------------------------
        # 7. Confirmation
        # ---------------------------------------------------------------------

        confirmations = (
            self.confirmation_engine.analyze(
                blocks
            )
        )

        confirmed_blocks = [

            confirmation.order_block

            for confirmation in confirmations

            if confirmation.confirmed

        ]

        # ---------------------------------------------------------------------
        # 8. Final confidence
        # ---------------------------------------------------------------------

        confidence = (
            self.confidence_engine.calculate(
                blocks
            )
        )

        # ---------------------------------------------------------------------
        # 9. Build map
        # ---------------------------------------------------------------------

        order_block_map = (
            self.map_engine.build(
                blocks=blocks,
                breakers=breakers,
            )
        )

        # ---------------------------------------------------------------------
        # 10. Direction
        # ---------------------------------------------------------------------

        direction = (
            self._determine_direction(
                confirmed_blocks
            )
        )

        # ---------------------------------------------------------------------
        # Probability
        # ---------------------------------------------------------------------

        probability = (
            self._calculate_probability(
                confirmed_blocks
                if confirmed_blocks
                else blocks
            )
        )

        # ---------------------------------------------------------------------
        # Strongest blocks
        # ---------------------------------------------------------------------

        strongest = (
            strongest_order_block(
                confirmed_blocks
                if confirmed_blocks
                else blocks
            )
        )

        bullish_confirmed = [

            block

            for block in confirmed_blocks

            if block.direction
            == OrderBlockDirection.BULLISH

        ]

        bearish_confirmed = [

            block

            for block in confirmed_blocks

            if block.direction
            == OrderBlockDirection.BEARISH

        ]

        strongest_bullish = (
            strongest_order_block(
                bullish_confirmed
            )
        )

        strongest_bearish = (
            strongest_order_block(
                bearish_confirmed
            )
        )

        # ---------------------------------------------------------------------
        # Reasons
        # ---------------------------------------------------------------------

        reasons = (
            self._build_reasons(
                bullish=bullish_blocks,
                bearish=bearish_blocks,
                breakers=breakers,
                confirmed=confirmed_blocks,
                confidence=confidence,
                probability=probability,
            )
        )

        # ---------------------------------------------------------------------
        # Final analysis
        # ---------------------------------------------------------------------

        analysis = OrderBlockAnalysis(

            direction=direction,

            confidence=confidence,

            probability=probability,

            order_block_map=order_block_map,

            reasons=reasons,

            strongest_block=strongest,

            strongest_bullish=strongest_bullish,

            strongest_bearish=strongest_bearish,

            confirmed_blocks=confirmed_blocks,

        )

        # ---------------------------------------------------------------------
        # Agent result
        # ---------------------------------------------------------------------

        result = AgentResult(

            name=self.AGENT_NAME,

            confidence=confidence,

            success=True,

            analysis=analysis,

        )

        # ---------------------------------------------------------------------
        # Shared memory
        # ---------------------------------------------------------------------

        self._store_result(
            context,
            result,
        )

        return result

    # =========================================================================
    # DIRECTION
    # =========================================================================

    @staticmethod
    def _determine_direction(
        blocks: list[OrderBlock],
    ) -> OrderBlockDirection:

        if not blocks:
            return OrderBlockDirection.NEUTRAL

        bullish = 0

        bearish = 0

        for block in blocks:

            if (
                block.direction
                == OrderBlockDirection.BULLISH
            ):
                bullish += 1

            elif (
                block.direction
                == OrderBlockDirection.BEARISH
            ):
                bearish += 1

        if bullish > bearish:
            return OrderBlockDirection.BULLISH

        if bearish > bullish:
            return OrderBlockDirection.BEARISH

        return OrderBlockDirection.NEUTRAL

    # =========================================================================
    # PROBABILITY
    # =========================================================================

    @staticmethod
    def _calculate_probability(
        blocks: list[OrderBlock],
    ) -> float:

        if not blocks:
            return 0.0

        total = sum(
            float(block.probability)
            for block in blocks
        )

        return round(
            total / len(blocks),
            2,
        )

    # =========================================================================
    # REASONS
    # =========================================================================

    @staticmethod
    def _build_reasons(
        bullish: list[OrderBlock],
        bearish: list[OrderBlock],
        breakers: list[OrderBlock],
        confirmed: list[OrderBlock],
        confidence: float,
        probability: float,
    ) -> list[str]:

        return [

            f"Bullish Order Blocks: "
            f"{len(bullish)}",

            f"Bearish Order Blocks: "
            f"{len(bearish)}",

            f"Breaker Blocks: "
            f"{len(breakers)}",

            f"Confirmed Blocks: "
            f"{len(confirmed)}",

            f"Average Probability: "
            f"{probability:.2f}",

            f"Overall Confidence: "
            f"{confidence:.2f}",

        ]

    # =========================================================================
    # EMPTY ANALYSIS
    # =========================================================================

    @staticmethod
    def _empty_analysis() -> OrderBlockAnalysis:

        from ai.agents.order_block.models import (
            OrderBlockMap,
        )

        empty_map = OrderBlockMap(

            bullish=[],

            bearish=[],

            breakers=[],

            mitigated=[],

            fresh=[],

            tested=[],

            invalid=[],

            all_blocks=[],

        )

        return OrderBlockAnalysis(

            direction=(
                OrderBlockDirection.NEUTRAL
            ),

            confidence=0.0,

            probability=0.0,

            order_block_map=empty_map,

            reasons=[
                "No Order Blocks Detected"
            ],

            strongest_block=None,

            strongest_bullish=None,

            strongest_bearish=None,

            confirmed_blocks=[],

        )

    # =========================================================================
    # CONTEXT STORAGE
    # =========================================================================

    @staticmethod
    def _store_result(
        context: MarketContext,
        result: AgentResult,
    ) -> None:

        context.memory["order_block"] = {
            "analysis": result.analysis,
            "confidence": result.confidence,
            "success": result.success,
        }

        context.add_result(
            result
        )
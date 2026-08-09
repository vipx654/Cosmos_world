"""
===============================================================================
COSMOS Smart Money Concept Engine

Institutional Smart Money Concept Orchestrator

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.context import MarketContext
from ai.models import AgentResult

from ai.agents.smc.models import (
    SMCAnalysis,
)

from ai.agents.smc.validator import (
    SMCValidator,
)

from ai.agents.smc.dealing_range_engine import (
    DealingRangeEngine,
)

from ai.agents.smc.premium_discount_engine import (
    PremiumDiscountEngine,
)

from ai.agents.smc.fvg_engine import (
    FVGEngine,
)

from ai.agents.smc.inducement_engine import (
    InducementEngine,
)

from ai.agents.smc.equal_high_low_engine import (
    EqualHighLowEngine,
)

from ai.agents.smc.confidence_engine import (
    ConfidenceEngine,
)


class SMCEngine:
    """
    Institutional Smart Money Concept AI.
    """

    def __init__(self):

        self.dealing_range_engine = (
            DealingRangeEngine()
        )

        self.premium_discount_engine = (
            PremiumDiscountEngine()
        )

        self.fvg_engine = (
            FVGEngine()
        )

        self.inducement_engine = (
            InducementEngine()
        )

        self.equal_engine = (
            EqualHighLowEngine()
        )

        self.confidence_engine = (
            ConfidenceEngine()
        )

    def analyze(
        self,
        context: MarketContext,
    ) -> AgentResult:

        SMCValidator.validate(context)

        # ---------------------------------------------------------
        # Shared Memory
        # ---------------------------------------------------------

        swings = context.memory["trend"]["swings"]

        # ---------------------------------------------------------
        # Current Price
        # ---------------------------------------------------------

        current_price = (
            context.candles[-1].close
        )

        # ---------------------------------------------------------
        # Dealing Range
        # ---------------------------------------------------------

        dealing_range = (

            self.dealing_range_engine.analyze(

                swings
            )
        )

        # ---------------------------------------------------------
        # Premium Discount
        # ---------------------------------------------------------

        premium_discount = (

            self.premium_discount_engine.analyze(

                current_price,

                dealing_range,
            )
        )

        # ---------------------------------------------------------
        # Fair Value Gap
        # ---------------------------------------------------------

        fvg = (

            self.fvg_engine.analyze(

                context.candles,
            )
        )

        # ---------------------------------------------------------
        # Inducement
        # ---------------------------------------------------------

        inducement = (

            self.inducement_engine.analyze(

                swings,
            )
        )

        # ---------------------------------------------------------
        # Equal Levels
        # ---------------------------------------------------------

        equal_high, equal_low = (

            self.equal_engine.analyze(

                swings,
            )
        )

        # ---------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------

        confidence = (

            self.confidence_engine.calculate(

                dealing_range,

                premium_discount,

                fvg,

                equal_high,

                equal_low,

                inducement,
            )
        )

        # ---------------------------------------------------------
        # Save Memory
        # ---------------------------------------------------------

        context.memory["smc"] = {

            "dealing_range": dealing_range,

            "premium_discount": premium_discount,

            "fvg": fvg,

            "equal_high": equal_high,

            "equal_low": equal_low,

            "inducement": inducement,

            "confidence": confidence,
        }

        # ---------------------------------------------------------
        # Final Analysis
        # ---------------------------------------------------------

        analysis = SMCAnalysis(

            dealing_range=dealing_range,

            premium_discount=premium_discount,

            fvg=fvg,

            equal_high=equal_high,

            equal_low=equal_low,

            inducement=inducement,

            confidence=confidence,

            reasons=[

                f"Zone : {premium_discount.zone.value}",

                f"FVG : {fvg.gap_type.value}",

                f"Inducement : {inducement.inducement_type.value}",

                f"Confidence : {confidence:.2f}",
            ],
        )

        result = AgentResult(

            name="smc",

            success=True,

            confidence=confidence,

            analysis=analysis,
        )

        context.add_result(result)

        return result
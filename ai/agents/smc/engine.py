"""
===============================================================================
COSMOS Smart Money Concept Engine

Institutional Smart Money Concept Orchestrator.

The SMC engine coordinates:
    - Dealing range
    - Premium / discount
    - Fair Value Gap
    - Inducement
    - Equal highs / lows
    - Confidence

The dedicated FVG agent remains the source of FVG detection.
This engine adapts its result into the SMC-specific FairValueGap model.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from typing import Any

from ai.context import MarketContext
from ai.models import AgentResult

from ai.agents.smc.models import (
    FairValueGap,
    FVGStatus,
    FVGType,
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

from ai.agents.fvg.engine import (
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

    The SMC engine uses the existing dedicated FVG agent instead of
    maintaining a duplicate FVG implementation inside the SMC package.
    """

    def __init__(self) -> None:

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

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        context: MarketContext,
    ) -> AgentResult:

        # ---------------------------------------------------------------------
        # 1. Validate context.
        # ---------------------------------------------------------------------

        SMCValidator.validate(
            context
        )

        # ---------------------------------------------------------------------
        # 2. Shared trend memory.
        # ---------------------------------------------------------------------

        swings = (
            context.memory["trend"]["swings"]
        )

        # ---------------------------------------------------------------------
        # 3. Current price.
        # ---------------------------------------------------------------------

        current_price = float(
            context.candles[-1].close
        )

        # ---------------------------------------------------------------------
        # 4. Dealing range.
        # ---------------------------------------------------------------------

        dealing_range = (
            self.dealing_range_engine.analyze(
                swings
            )
        )

        # ---------------------------------------------------------------------
        # 5. Premium / discount.
        # ---------------------------------------------------------------------

        premium_discount = (
            self.premium_discount_engine.analyze(
                current_price,
                dealing_range,
            )
        )

        # ---------------------------------------------------------------------
        # 6. Dedicated FVG agent.
        # ---------------------------------------------------------------------

        raw_fvg = (
            self.fvg_engine.analyze(
                context
            )
        )

        # ---------------------------------------------------------------------
        # 7. Adapt standalone FVG result into the SMC model.
        # ---------------------------------------------------------------------

        fvg = self._adapt_fvg(
            raw_fvg
        )

        # ---------------------------------------------------------------------
        # 8. Inducement.
        # ---------------------------------------------------------------------

        inducement = (
            self.inducement_engine.analyze(
                swings
            )
        )

        # ---------------------------------------------------------------------
        # 9. Equal highs / lows.
        # ---------------------------------------------------------------------

        equal_high, equal_low = (
            self.equal_engine.analyze(
                swings
            )
        )

        # ---------------------------------------------------------------------
        # 10. Confidence.
        # ---------------------------------------------------------------------

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

        confidence = float(
            confidence
        )

        # ---------------------------------------------------------------------
        # 11. Save SMC memory.
        # ---------------------------------------------------------------------

        context.memory["smc"] = {

            "dealing_range": (
                dealing_range
            ),

            "premium_discount": (
                premium_discount
            ),

            "fvg": fvg,

            "equal_high": (
                equal_high
            ),

            "equal_low": (
                equal_low
            ),

            "inducement": (
                inducement
            ),

            "confidence": confidence,
        }

        # ---------------------------------------------------------------------
        # 12. Final SMC analysis.
        # ---------------------------------------------------------------------

        analysis = SMCAnalysis(

            dealing_range=(
                dealing_range
            ),

            premium_discount=(
                premium_discount
            ),

            fvg=fvg,

            equal_high=(
                equal_high
            ),

            equal_low=(
                equal_low
            ),

            inducement=(
                inducement
            ),

            confidence=confidence,

            reasons=[
                (
                    f"Zone : "
                    f"{premium_discount.zone.value}"
                ),

                (
                    f"FVG : "
                    f"{fvg.gap_type.value}"
                ),

                (
                    f"Inducement : "
                    f"{inducement.inducement_type.value}"
                ),

                (
                    f"Confidence : "
                    f"{confidence:.2f}"
                ),
            ],
        )

        # ---------------------------------------------------------------------
        # 13. Agent result.
        # ---------------------------------------------------------------------

        result = AgentResult(

            name="smc",

            success=True,

            confidence=confidence,

            analysis=analysis,
        )

        context.add_result(
            result
        )

        return result

    # =========================================================================
    # FVG ADAPTER
    # =========================================================================

    @staticmethod
    def _adapt_fvg(
        raw_fvg: Any,
    ) -> FairValueGap:
        """
        Convert the standalone FVG agent's result into the SMC FairValueGap
        model.

        The SMC model requires:

            gap_type
            status
            upper
            lower

        The standalone FVG agent may expose the strongest FVG through
        `strongest_fvg`, or expose a direction/map containing the detected FVG.

        When no actionable FVG exists, a neutral SMC FVG is returned.
        """

        if raw_fvg is None:

            return FairValueGap(
                gap_type=FVGType.NONE,
                status=FVGStatus.INVALID,
                upper=0.0,
                lower=0.0,
            )

        strongest = getattr(
            raw_fvg,
            "strongest_fvg",
            None,
        )

        if strongest is None:

            confirmed = getattr(
                raw_fvg,
                "confirmed_fvgs",
                None,
            )

            if confirmed:

                strongest = confirmed[0]

        if strongest is None:

            return FairValueGap(
                gap_type=FVGType.NONE,
                status=FVGStatus.INVALID,
                upper=0.0,
                lower=0.0,
            )

        # ---------------------------------------------------------------------
        # Direction
        # ---------------------------------------------------------------------

        direction = getattr(
            strongest,
            "direction",
            None,
        )

        direction_value = (
            getattr(
                direction,
                "value",
                direction,
            )
        )

        direction_value = str(
            direction_value
        ).lower()

        if "bull" in direction_value:

            gap_type = (
                FVGType.BULLISH
            )

        elif "bear" in direction_value:

            gap_type = (
                FVGType.BEARISH
            )

        else:

            gap_type = (
                FVGType.NONE
            )

        # ---------------------------------------------------------------------
        # Price boundaries
        # ---------------------------------------------------------------------

        upper = (
            getattr(
                strongest,
                "upper",
                None,
            )
        )

        lower = (
            getattr(
                strongest,
                "lower",
                None,
            )
        )

        if upper is None:

            upper = getattr(
                strongest,
                "gap_high",
                None,
            )

        if lower is None:

            lower = getattr(
                strongest,
                "gap_low",
                None,
            )

        # Some FVG models expose high/low instead.
        if upper is None:

            upper = getattr(
                strongest,
                "high",
                0.0,
            )

        if lower is None:

            lower = getattr(
                strongest,
                "low",
                0.0,
            )

        try:

            upper = float(
                upper
            )

        except (
            TypeError,
            ValueError,
        ):

            upper = 0.0

        try:

            lower = float(
                lower
            )

        except (
            TypeError,
            ValueError,
        ):

            lower = 0.0

        # ---------------------------------------------------------------------
        # Status
        # ---------------------------------------------------------------------

        raw_status = getattr(
            strongest,
            "status",
            None,
        )

        status_value = str(
            getattr(
                raw_status,
                "value",
                raw_status,
            )
        ).lower()

        if (
            "partial"
            in status_value
        ):

            status = FVGStatus.PARTIAL

        elif (
            "filled"
            in status_value
        ):

            status = FVGStatus.FILLED

        elif (
            "invalid"
            in status_value
        ):

            status = FVGStatus.INVALID

        else:

            status = FVGStatus.ACTIVE

        # ---------------------------------------------------------------------
        # Neutral fallback
        # ---------------------------------------------------------------------

        if (
            gap_type
            == FVGType.NONE
        ):

            status = (
                FVGStatus.INVALID
            )

        return FairValueGap(

            gap_type=gap_type,

            status=status,

            upper=upper,

            lower=lower,
        )
        

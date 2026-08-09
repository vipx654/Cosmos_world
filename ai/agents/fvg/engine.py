"""
===============================================================================
COSMOS Fair Value Gap Engine

Main orchestration engine for Fair Value Gap analysis.

Pipeline:

    Validation
        ↓
    Bullish / Bearish Detection
        ↓
    Mitigation
        ↓
    Inversion
        ↓
    Confirmation
        ↓
    Probability
        ↓
    Confidence
        ↓
    FVG Map
        ↓
    FVG Analysis

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.bullish_fvg import (
    BullishFVGEngine,
)

from ai.agents.fvg.bearish_fvg import (
    BearishFVGEngine,
)

from ai.agents.fvg.confirmation_engine import (
    ConfirmationEngine,
)

from ai.agents.fvg.confidence_engine import (
    ConfidenceEngine,
)

from ai.agents.fvg.fvg_map import (
    FVGMapEngine,
)

from ai.agents.fvg.inversion_engine import (
    InversionEngine,
)

from ai.agents.fvg.mitigation_engine import (
    MitigationEngine,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGAnalysis,
    FVGDirection,
)

from ai.agents.fvg.probability_engine import (
    ProbabilityEngine,
)

from ai.agents.fvg.validator import (
    FVGValidator,
)

from ai.agents.fvg.utils import (
    strongest_fvg,
)


class FVGEngine:
    """
    Main Fair Value Gap Agent engine.

    This class connects every FVG component without embedding the individual
    detection/analysis rules directly inside the orchestrator.
    """

    def __init__(self) -> None:

        self.validator = (
            FVGValidator()
        )

        self.bullish_engine = (
            BullishFVGEngine()
        )

        self.bearish_engine = (
            BearishFVGEngine()
        )

        self.mitigation_engine = (
            MitigationEngine()
        )

        self.inversion_engine = (
            InversionEngine()
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
            FVGMapEngine()
        )

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        context,
    ) -> FVGAnalysis:
        """
        Execute the complete FVG analysis pipeline.
        """

        # ---------------------------------------------------------------------
        # 1. Validate market context.
        # ---------------------------------------------------------------------

        self.validator.validate(
            context
        )

        candles = context.candles

        # ---------------------------------------------------------------------
        # 2. Detect bullish FVGs.
        # ---------------------------------------------------------------------

        bullish = (
            self.bullish_engine.analyze(
                candles
            )
        )

        # ---------------------------------------------------------------------
        # 3. Detect bearish FVGs.
        # ---------------------------------------------------------------------

        bearish = (
            self.bearish_engine.analyze(
                candles
            )
        )

        # ---------------------------------------------------------------------
        # 4. Combine detections.
        # ---------------------------------------------------------------------

        fvgs: list[FairValueGap] = (
            bullish + bearish
        )

        # ---------------------------------------------------------------------
        # 5. Mitigation analysis.
        # ---------------------------------------------------------------------

        self.mitigation_engine.analyze(
            fvgs,
            candles,
        )

        # ---------------------------------------------------------------------
        # 6. Inversion analysis.
        # ---------------------------------------------------------------------

        self.inversion_engine.analyze(
            fvgs,
            candles,
        )

        # ---------------------------------------------------------------------
        # 7. Confirmation.
        # ---------------------------------------------------------------------

        confirmations = (
            self.confirmation_engine.analyze(
                fvgs
            )
        )

        # ---------------------------------------------------------------------
        # 8. Probability.
        # ---------------------------------------------------------------------

        self.probability_engine.analyze(
            fvgs
        )

        # ---------------------------------------------------------------------
        # 9. Final confidence.
        # ---------------------------------------------------------------------

        self.confidence_engine.analyze(
            fvgs
        )

        # ---------------------------------------------------------------------
        # 10. Build organized map.
        # ---------------------------------------------------------------------

        fvg_map = (
            self.map_engine.build(
                fvgs
            )
        )

        # ---------------------------------------------------------------------
        # 11. Confirmed FVGs.
        # ---------------------------------------------------------------------

        confirmed_fvgs = [
            confirmation.fvg
            for confirmation in confirmations
            if confirmation.confirmed
        ]

        # ---------------------------------------------------------------------
        # 12. Determine strongest FVG.
        # ---------------------------------------------------------------------

        strongest = strongest_fvg(
            confirmed_fvgs
        )

        # ---------------------------------------------------------------------
        # 13. Determine directional bias.
        # ---------------------------------------------------------------------

        bullish_confirmed = [
            fvg
            for fvg in confirmed_fvgs
            if fvg.direction
            == FVGDirection.BULLISH
        ]

        bearish_confirmed = [
            fvg
            for fvg in confirmed_fvgs
            if fvg.direction
            == FVGDirection.BEARISH
        ]

        strongest_bullish = (
            strongest_fvg(
                bullish_confirmed
            )
        )

        strongest_bearish = (
            strongest_fvg(
                bearish_confirmed
            )
        )

        # ---------------------------------------------------------------------
        # Direction decision.
        # ---------------------------------------------------------------------

        direction = (
            FVGDirection.NEUTRAL
        )

        if (
            strongest_bullish is not None
            and
            strongest_bearish is None
        ):

            direction = (
                FVGDirection.BULLISH
            )

        elif (
            strongest_bearish is not None
            and
            strongest_bullish is None
        ):

            direction = (
                FVGDirection.BEARISH
            )

        elif (
            strongest_bullish is not None
            and
            strongest_bearish is not None
        ):

            if (
                strongest_bullish.confidence
                >
                strongest_bearish.confidence
            ):

                direction = (
                    FVGDirection.BULLISH
                )

            elif (
                strongest_bearish.confidence
                >
                strongest_bullish.confidence
            ):

                direction = (
                    FVGDirection.BEARISH
                )

        # ---------------------------------------------------------------------
        # Aggregate confidence.
        # ---------------------------------------------------------------------

        if confirmed_fvgs:

            confidence = round(
                sum(
                    fvg.confidence
                    for fvg in confirmed_fvgs
                )
                /
                len(confirmed_fvgs),
                2,
            )

            probability = round(
                sum(
                    fvg.probability
                    for fvg in confirmed_fvgs
                )
                /
                len(confirmed_fvgs),
                2,
            )

        else:

            confidence = 0.0

            probability = 0.0

        # ---------------------------------------------------------------------
        # Analysis reasons.
        # ---------------------------------------------------------------------

        reasons: list[str] = []

        if bullish:

            reasons.append(
                f"{len(bullish)} Bullish FVG(s) detected"
            )

        if bearish:

            reasons.append(
                f"{len(bearish)} Bearish FVG(s) detected"
            )

        if confirmed_fvgs:

            reasons.append(
                f"{len(confirmed_fvgs)} FVG(s) confirmed"
            )

        if fvg_map.fresh:

            reasons.append(
                f"{len(fvg_map.fresh)} Fresh FVG(s)"
            )

        if fvg_map.partial:

            reasons.append(
                f"{len(fvg_map.partial)} Partially mitigated FVG(s)"
            )

        if fvg_map.filled:

            reasons.append(
                f"{len(fvg_map.filled)} Filled FVG(s)"
            )

        if fvg_map.inverted:

            reasons.append(
                f"{len(fvg_map.inverted)} Inverted FVG(s)"
            )

        if direction != FVGDirection.NEUTRAL:

            reasons.append(
                f"FVG Direction: {direction.value}"
            )

        if not reasons:

            reasons.append(
                "No actionable FVG detected"
            )

        # ---------------------------------------------------------------------
        # Final result.
        # ---------------------------------------------------------------------

        return FVGAnalysis(

            direction=direction,

            confidence=confidence,

            probability=probability,

            fvg_map=fvg_map,

            reasons=reasons,

            strongest_fvg=strongest,

            strongest_bullish=(
                strongest_bullish
            ),

            strongest_bearish=(
                strongest_bearish
            ),

            confirmed_fvgs=confirmed_fvgs,

        )
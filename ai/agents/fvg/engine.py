"""
===============================================================================
COSMOS Fair Value Gap Engine

Main orchestration engine for Fair Value Gap analysis.

Pipeline:

    Validation
        ↓
    Bullish / Bearish Detection
        ↓
    Detection Merge
        ↓
    Mitigation
        ↓
    Inversion
        ↓
    Probability
        ↓
    Confidence
        ↓
    Confirmation
        ↓
    FVG Map
        ↓
    Ranking / Direction
        ↓
    FVG Analysis

Design goals:

    - Deterministic pipeline execution
    - Correct dependency ordering
    - No duplicated FVG logic inside the orchestrator
    - Stable FVGAnalysis contract
    - Correct post-inversion directional handling
    - Confirmation based on finalized probability/confidence
    - Safe handling of empty detection results
    - Future-ready architecture for:
        * BOS / CHOCH
        * liquidity sweeps
        * order blocks
        * HTF confluence
        * session analysis
        * volume
        * adaptive scoring
        * historical calibration

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

from ai.agents.fvg.utils import (
    strongest_fvg,
)

from ai.agents.fvg.validator import (
    FVGValidator,
)


class FVGEngine:
    """
    Main Fair Value Gap orchestration engine.

    The engine coordinates the individual FVG components but deliberately
    keeps detection, mitigation, inversion, probability and confirmation
    logic inside their dedicated modules.

    This makes the orchestrator stable while allowing individual FVG
    intelligence modules to evolve independently.
    """

    def __init__(self) -> None:
        """
        Initialize all FVG analysis components.
        """

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

        self.probability_engine = (
            ProbabilityEngine()
        )

        self.confidence_engine = (
            ConfidenceEngine()
        )

        self.confirmation_engine = (
            ConfirmationEngine()
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

        Pipeline ordering is intentional:

            detection
                ↓
            mitigation
                ↓
            inversion
                ↓
            probability
                ↓
            confidence
                ↓
            confirmation
                ↓
            mapping
                ↓
            ranking
                ↓
            final analysis

        Probability and confidence are calculated BEFORE confirmation so the
        confirmation engine evaluates the finalized FVG scores instead of
        default/stale values.
        """

        # =====================================================================
        # 1. VALIDATE CONTEXT
        # =====================================================================

        self.validator.validate(
            context
        )

        candles = context.candles

        # =====================================================================
        # 2. DETECT BULLISH FVGs
        # =====================================================================

        bullish_fvgs = (
            self.bullish_engine.analyze(
                candles
            )
        )

        # =====================================================================
        # 3. DETECT BEARISH FVGs
        # =====================================================================

        bearish_fvgs = (
            self.bearish_engine.analyze(
                candles
            )
        )

        # =====================================================================
        # 4. MERGE DETECTIONS
        # =====================================================================

        fvgs: list[FairValueGap] = [
            *bullish_fvgs,
            *bearish_fvgs,
        ]

        # =====================================================================
        # FAST EMPTY RESULT
        #
        # Avoid running unnecessary downstream engines when no FVG exists.
        # =====================================================================

        if not fvgs:
            fvg_map = (
                self.map_engine.build(
                    []
                )
            )

            return FVGAnalysis(
                direction=FVGDirection.NEUTRAL,
                confidence=0.0,
                probability=0.0,
                fvg_map=fvg_map,
                reasons=[
                    "No actionable FVG detected"
                ],
                strongest_fvg=None,
                strongest_bullish=None,
                strongest_bearish=None,
                confirmed_fvgs=[],
            )

        # =====================================================================
        # 5. MITIGATION
        #
        # Determines whether each FVG is:
        #
        #     untouched
        #     tested
        #     partially filled
        #     fully filled
        # =====================================================================

        self.mitigation_engine.analyze(
            fvgs,
            candles,
        )

        # =====================================================================
        # 6. INVERSION
        #
        # Inversion is evaluated after mitigation because the current market
        # interaction should be reflected before the directional thesis is
        # finalized.
        # =====================================================================

        self.inversion_engine.analyze(
            fvgs,
            candles,
        )

        # =====================================================================
        # 7. PROBABILITY
        #
        # Probability consumes the current FVG state after mitigation and
        # inversion.
        # =====================================================================

        self.probability_engine.analyze(
            fvgs
        )

        # =====================================================================
        # 8. FINAL CONFIDENCE
        #
        # Confidence consumes the updated probability and strength values.
        # This must happen before confirmation.
        # =====================================================================

        self.confidence_engine.analyze(
            fvgs
        )

        # =====================================================================
        # 9. CONFIRMATION
        #
        # Confirmation now evaluates the finalized confidence/probability
        # instead of the initial/default values.
        # =====================================================================

        confirmations = (
            self.confirmation_engine.analyze(
                fvgs
            )
        )

        # =====================================================================
        # 10. BUILD FVG MAP
        #
        # Mapping is deliberately performed after all state-changing engines
        # have completed.
        # =====================================================================

        fvg_map = (
            self.map_engine.build(
                fvgs
            )
        )

        # =====================================================================
        # 11. EXTRACT CONFIRMED FVGs
        # =====================================================================

        confirmed_fvgs = [
            confirmation.fvg
            for confirmation in confirmations
            if confirmation.confirmed
        ]

        # =====================================================================
        # 12. RANK STRONGEST CONFIRMED FVG
        # =====================================================================

        strongest = strongest_fvg(
            confirmed_fvgs
        )

        # =====================================================================
        # 13. SPLIT CONFIRMED FVGs BY DIRECTION
        #
        # Direction is evaluated AFTER inversion because an inverted FVG may
        # legitimately change its active directional thesis.
        # =====================================================================

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

        # =====================================================================
        # 14. FIND STRONGEST DIRECTIONAL FVG
        # =====================================================================

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

        # =====================================================================
        # 15. DETERMINE DIRECTIONAL BIAS
        # =====================================================================

        direction = (
            self._determine_direction(
                strongest_bullish,
                strongest_bearish,
            )
        )

        # =====================================================================
        # 16. AGGREGATE FINAL SCORES
        # =====================================================================

        confidence = (
            self._average_confidence(
                confirmed_fvgs
            )
        )

        probability = (
            self._average_probability(
                confirmed_fvgs
            )
        )

        # =====================================================================
        # 17. BUILD ANALYSIS REASONS
        # =====================================================================

        reasons = (
            self._build_reasons(
                bullish_fvgs=bullish_fvgs,
                bearish_fvgs=bearish_fvgs,
                confirmed_fvgs=confirmed_fvgs,
                fvg_map=fvg_map,
                direction=direction,
            )
        )

        # =====================================================================
        # 18. FINAL RESULT
        # =====================================================================

        return FVGAnalysis(
            direction=direction,
            confidence=confidence,
            probability=probability,
            fvg_map=fvg_map,
            reasons=reasons,
            strongest_fvg=strongest,
            strongest_bullish=strongest_bullish,
            strongest_bearish=strongest_bearish,
            confirmed_fvgs=confirmed_fvgs,
        )

    # =========================================================================
    # DIRECTION
    # =========================================================================

    @staticmethod
    def _determine_direction(
        strongest_bullish: FairValueGap | None,
        strongest_bearish: FairValueGap | None,
    ) -> FVGDirection:
        """
        Determine the dominant confirmed FVG direction.

        If both directions exist, confidence is used as the primary
        discriminator and probability is used as a secondary discriminator.

        Exact ties remain NEUTRAL rather than creating an artificial bias.
        """

        if (
            strongest_bullish is None
            and
            strongest_bearish is None
        ):
            return FVGDirection.NEUTRAL

        if (
            strongest_bullish is not None
            and
            strongest_bearish is None
        ):
            return FVGDirection.BULLISH

        if (
            strongest_bearish is not None
            and
            strongest_bullish is None
        ):
            return FVGDirection.BEARISH

        bullish_confidence = float(
            strongest_bullish.confidence
        )

        bearish_confidence = float(
            strongest_bearish.confidence
        )

        if (
            bullish_confidence
            >
            bearish_confidence
        ):
            return FVGDirection.BULLISH

        if (
            bearish_confidence
            >
            bullish_confidence
        ):
            return FVGDirection.BEARISH

        bullish_probability = float(
            strongest_bullish.probability
        )

        bearish_probability = float(
            strongest_bearish.probability
        )

        if (
            bullish_probability
            >
            bearish_probability
        ):
            return FVGDirection.BULLISH

        if (
            bearish_probability
            >
            bullish_probability
        ):
            return FVGDirection.BEARISH

        return FVGDirection.NEUTRAL

    # =========================================================================
    # SCORE AGGREGATION
    # =========================================================================

    @staticmethod
    def _average_confidence(
        fvgs: list[FairValueGap],
    ) -> float:
        """
        Calculate average confidence of confirmed FVGs.
        """

        if not fvgs:
            return 0.0

        return round(
            sum(
                float(fvg.confidence)
                for fvg in fvgs
            )
            / len(fvgs),
            2,
        )

    @staticmethod
    def _average_probability(
        fvgs: list[FairValueGap],
    ) -> float:
        """
        Calculate average probability of confirmed FVGs.
        """

        if not fvgs:
            return 0.0

        return round(
            sum(
                float(fvg.probability)
                for fvg in fvgs
            )
            / len(fvgs),
            2,
        )

    # =========================================================================
    # REASONS
    # =========================================================================

    @staticmethod
    def _build_reasons(
        bullish_fvgs: list[FairValueGap],
        bearish_fvgs: list[FairValueGap],
        confirmed_fvgs: list[FairValueGap],
        fvg_map,
        direction: FVGDirection,
    ) -> list[str]:
        """
        Build a concise explanation of the final FVG analysis.
        """

        reasons: list[str] = []

        # ---------------------------------------------------------------------
        # Detection
        # ---------------------------------------------------------------------

        if bullish_fvgs:
            reasons.append(
                f"{len(bullish_fvgs)} Bullish FVG(s) detected"
            )

        if bearish_fvgs:
            reasons.append(
                f"{len(bearish_fvgs)} Bearish FVG(s) detected"
            )

        # ---------------------------------------------------------------------
        # Confirmation
        # ---------------------------------------------------------------------

        if confirmed_fvgs:
            reasons.append(
                f"{len(confirmed_fvgs)} FVG(s) confirmed"
            )

        # ---------------------------------------------------------------------
        # Lifecycle
        # ---------------------------------------------------------------------

        if fvg_map.fresh:
            reasons.append(
                f"{len(fvg_map.fresh)} Fresh FVG(s)"
            )

        if fvg_map.tested:
            reasons.append(
                f"{len(fvg_map.tested)} Tested FVG(s)"
            )

        if fvg_map.partial:
            reasons.append(
                f"{len(fvg_map.partial)} Partially mitigated FVG(s)"
            )

        if fvg_map.filled:
            reasons.append(
                f"{len(fvg_map.filled)} Filled FVG(s)"
            )

        if fvg_map.invalid:
            reasons.append(
                f"{len(fvg_map.invalid)} Invalid FVG(s)"
            )

        # ---------------------------------------------------------------------
        # Inversion
        # ---------------------------------------------------------------------

        if fvg_map.inverted:
            reasons.append(
                f"{len(fvg_map.inverted)} Inverted FVG(s)"
            )

        # ---------------------------------------------------------------------
        # Direction
        # ---------------------------------------------------------------------

        if direction != FVGDirection.NEUTRAL:
            reasons.append(
                f"FVG Direction: {direction.value}"
            )

        # ---------------------------------------------------------------------
        # Fallback
        # ---------------------------------------------------------------------

        if not reasons:
            reasons.append(
                "No actionable FVG detected"
            )

        return reasons

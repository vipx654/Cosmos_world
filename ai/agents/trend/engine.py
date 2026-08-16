"""
===============================================================================
COSMOS Trend Engine
===============================================================================

Production-grade Trend Intelligence Coordinator.

Pipeline:

    Market Candles
         ↓
    Data Validation
         ↓
    Swing Detection
         ↓
    Dow Structure
         ↓
    EMA Regime
         ↓
    Momentum
         ↓
    Trendline
         ↓
    Evidence Fusion
         ↓
    Direction + Strength
         ↓
    Chart Intelligence / Annotations
         ↓
    Shared Trend Memory
         ↓
    AgentResult

Design goals:

    - Deterministic
    - Production ready
    - Downstream-agent compatible
    - Chart-annotation ready
    - Extensible for multi-timeframe analysis
    - Extensible for ML/AI confirmation
    - No API dependency
    - No standalone-indicator trading
    - Preserves existing COSMOS interfaces

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from time import perf_counter

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
    Production Trend Intelligence Engine.

    The Trend Engine does not directly place trades.

    Its responsibility is to determine:

        - market direction
        - market structure
        - momentum state
        - EMA regime
        - trendline state
        - trend strength
        - evidence confidence
        - structural chart annotations

    The resulting intelligence is published to:

        context.memory["trend"]

    Downstream agents may consume this memory.
    """

    AGENT_NAME = "trend"

    # Kept as metadata rather than being used for logic.
    AGENT_VERSION = "MAX"

    # -------------------------------------------------------------------------
    # Minimum market data
    # -------------------------------------------------------------------------

    MIN_CANDLES = 20

    # -------------------------------------------------------------------------
    # Structure requirements
    # -------------------------------------------------------------------------

    MIN_DIRECTION_STRUCTURES = 2

    # -------------------------------------------------------------------------
    # Confidence thresholds
    # -------------------------------------------------------------------------

    STRONG_CONFIDENCE = 85.0
    MEDIUM_CONFIDENCE = 65.0
    WEAK_CONFIDENCE = 45.0

    def __init__(
        self,
        swing_engine: SwingEngine | None = None,
        dow_engine: DowEngine | None = None,
        ema_engine: EMAEngine | None = None,
        momentum_engine: MomentumEngine | None = None,
        trendline_engine: TrendlineEngine | None = None,
        confidence_engine: ConfidenceEngine | None = None,
    ) -> None:

        self.swing_engine = (
            swing_engine
            or SwingEngine()
        )

        self.dow_engine = (
            dow_engine
            or DowEngine()
        )

        self.ema_engine = (
            ema_engine
            or EMAEngine()
        )

        self.momentum_engine = (
            momentum_engine
            or MomentumEngine()
        )

        self.trendline_engine = (
            trendline_engine
            or TrendlineEngine()
        )

        self.confidence_engine = (
            confidence_engine
            or ConfidenceEngine()
        )

    # =========================================================================
    # MAIN
    # =========================================================================

    def analyze(
        self,
        context: MarketContext,
    ) -> AgentResult:

        started = perf_counter()

        # ---------------------------------------------------------------------
        # Validation
        # ---------------------------------------------------------------------

        if context is None:
            raise ValueError(
                "MarketContext cannot be None."
            )

        TrendValidator.validate(context)

        if len(context.candles) < self.MIN_CANDLES:
            raise ValueError(
                "Trend Agent requires at least "
                f"{self.MIN_CANDLES} candles."
            )

        # ---------------------------------------------------------------------
        # 1. Swing Detection
        # ---------------------------------------------------------------------

        swings = self.swing_engine.detect(
            context.candles
        )

        # ---------------------------------------------------------------------
        # 2. Dow Theory
        # ---------------------------------------------------------------------

        structures = self.dow_engine.analyze(
            swings
        )

        # ---------------------------------------------------------------------
        # 3. EMA Regime
        # ---------------------------------------------------------------------

        ema = self.ema_engine.analyze(
            context.candles
        )

        # ---------------------------------------------------------------------
        # 4. Momentum
        # ---------------------------------------------------------------------

        momentum = self.momentum_engine.analyze(
            context.candles
        )

        # ---------------------------------------------------------------------
        # 5. Trendline
        # ---------------------------------------------------------------------

        trendline = self.trendline_engine.analyze(
            swings
        )

        # ---------------------------------------------------------------------
        # 6. Base Confidence
        # ---------------------------------------------------------------------

        confidence = self.confidence_engine.calculate(
            ema=ema,
            momentum=momentum,
            trendline=trendline,
        )

        confidence = self._clamp(
            confidence
        )

        # ---------------------------------------------------------------------
        # 7. Structural Direction
        # ---------------------------------------------------------------------

        structural_direction = (
            self._detect_structural_direction(
                structures
            )
        )

        # ---------------------------------------------------------------------
        # 8. Evidence Direction
        # ---------------------------------------------------------------------

        evidence_direction = (
            self._detect_evidence_direction(
                ema=ema,
                momentum=momentum,
                trendline=trendline,
            )
        )

        # ---------------------------------------------------------------------
        # 9. Final Direction
        # ---------------------------------------------------------------------

        direction = self._resolve_direction(
            structural_direction=structural_direction,
            evidence_direction=evidence_direction,
            ema_bullish=ema.bullish_alignment,
            ema_bearish=ema.bearish_alignment,
            momentum_bullish=momentum.bullish,
            momentum_bearish=momentum.bearish,
        )

        # ---------------------------------------------------------------------
        # 10. Evidence Quality
        # ---------------------------------------------------------------------

        agreement = self._calculate_agreement(
            direction=direction,
            structural_direction=structural_direction,
            evidence_direction=evidence_direction,
            ema_bullish=ema.bullish_alignment,
            ema_bearish=ema.bearish_alignment,
            momentum_bullish=momentum.bullish,
            momentum_bearish=momentum.bearish,
        )

        # ---------------------------------------------------------------------
        # 11. Confidence Adjustment
        #
        # Confidence should not blindly remain high when the engines disagree.
        # ---------------------------------------------------------------------

        confidence = self._adjust_confidence(
            confidence=confidence,
            agreement=agreement,
            direction=direction,
        )

        # ---------------------------------------------------------------------
        # 12. Trend Strength
        # ---------------------------------------------------------------------

        strength = self._calculate_strength(
            confidence=confidence,
            momentum_confidence=momentum.confidence,
            structure_count=len(structures),
            trendline_confidence=trendline.confidence,
            agreement=agreement,
        )

        # ---------------------------------------------------------------------
        # 13. Structure String
        # ---------------------------------------------------------------------

        structure_values = [
            structure.value
            for structure in structures
        ]

        structure_string = " → ".join(
            structure_values[-8:]
        )

        # ---------------------------------------------------------------------
        # 14. Acceleration
        # ---------------------------------------------------------------------

        acceleration = (
            momentum.acceleration > 0
            if direction == TrendDirection.BULLISH
            else (
                momentum.acceleration < 0
                if direction == TrendDirection.BEARISH
                else False
            )
        )

        # ---------------------------------------------------------------------
        # 15. Reasons
        # ---------------------------------------------------------------------

        reasons = self._build_reasons(
            direction=direction,
            structural_direction=structural_direction,
            evidence_direction=evidence_direction,
            ema=ema,
            momentum=momentum,
            trendline=trendline,
            agreement=agreement,
            confidence=confidence,
        )

        # ---------------------------------------------------------------------
        # 16. Final Analysis
        # ---------------------------------------------------------------------

        analysis = TrendAnalysis(

            direction=direction,

            confidence=confidence,

            strength=strength,

            structure=structure_string,

            structures=structure_values,

            acceleration=acceleration,

            momentum=momentum.velocity,

            reasons=reasons,
        )

        # ---------------------------------------------------------------------
        # 17. Chart Intelligence
        #
        # This is deliberately stored as structured data.
        #
        # Later the Cosmos UI can render:
        #
        #   - swing highs/lows
        #   - trendlines
        #   - EMA state
        #   - structure labels
        #   - trend direction
        #   - confidence
        #
        # When an agent locks an analysis, this payload can become
        # an immutable chart annotation.
        # ---------------------------------------------------------------------

        annotations = self._build_chart_annotations(
            context=context,
            swings=swings,
            structures=structures,
            trendline=trendline,
            ema=ema,
            direction=direction,
            confidence=confidence,
        )

        # ---------------------------------------------------------------------
        # 18. Execution Time
        # ---------------------------------------------------------------------

        execution_time_ms = (
            perf_counter() - started
        ) * 1000.0

        # ---------------------------------------------------------------------
        # 19. Agent Result
        # ---------------------------------------------------------------------

        result = AgentResult(

            name=self.AGENT_NAME,

            confidence=confidence,

            success=True,

            analysis=analysis,

            execution_time_ms=round(
                execution_time_ms,
                3,
            ),
        )

        # ---------------------------------------------------------------------
        # 20. Shared Memory
        # ---------------------------------------------------------------------

        context.memory["trend"] = {

            # Identity
            "agent": self.AGENT_NAME,
            "version": self.AGENT_VERSION,

            # Final interpretation
            "direction": direction,
            "confidence": confidence,
            "strength": strength,

            # Structure
            "structure": structure_string,
            "structures": structure_values,
            "structure_count": len(structures),

            # Raw structural data
            "swings": swings,

            # Engine outputs
            "ema": ema,
            "momentum_analysis": momentum,
            "trendline": trendline,

            # Derived state
            "acceleration": acceleration,
            "momentum": momentum.velocity,

            # Evidence
            "structural_direction": (
                structural_direction
            ),

            "evidence_direction": (
                evidence_direction
            ),

            "agreement": agreement,

            # Human-readable explanation
            "reasons": reasons,

            # Chart layer
            "annotations": annotations,

            # Result
            "analysis": analysis,
            "result": result,

            # Runtime
            "execution_time_ms": (
                round(
                    execution_time_ms,
                    3,
                )
            ),
        }

        # ---------------------------------------------------------------------
        # 21. Context Result
        # ---------------------------------------------------------------------

        context.add_result(
            result
        )

        return result

    # =========================================================================
    # STRUCTURAL DIRECTION
    # =========================================================================

    @staticmethod
    def _detect_structural_direction(
        structures: list[StructureType],
    ) -> TrendDirection:

        if len(structures) < 2:
            return TrendDirection.UNKNOWN

        bullish_score = 0
        bearish_score = 0

        # Evaluate recent structure with more weight.
        recent = structures[-8:]

        for index, structure in enumerate(recent):

            weight = index + 1

            if structure in (
                StructureType.HH,
                StructureType.HL,
            ):
                bullish_score += weight

            elif structure in (
                StructureType.LH,
                StructureType.LL,
            ):
                bearish_score += weight

        if bullish_score > bearish_score:
            return TrendDirection.BULLISH

        if bearish_score > bullish_score:
            return TrendDirection.BEARISH

        return TrendDirection.SIDEWAYS

    # =========================================================================
    # INDICATOR EVIDENCE
    # =========================================================================

    @staticmethod
    def _detect_evidence_direction(
        ema,
        momentum,
        trendline,
    ) -> TrendDirection:

        bullish = 0
        bearish = 0

        if ema.bullish_alignment:
            bullish += 2

        if ema.bearish_alignment:
            bearish += 2

        if momentum.bullish:
            bullish += 2

        if momentum.bearish:
            bearish += 2

        if trendline.bullish_trendline:
            bullish += 1

        if trendline.bearish_trendline:
            bearish += 1

        if bullish > bearish:
            return TrendDirection.BULLISH

        if bearish > bullish:
            return TrendDirection.BEARISH

        return TrendDirection.SIDEWAYS

    # =========================================================================
    # FINAL DIRECTION
    # =========================================================================

    @staticmethod
    def _resolve_direction(
        structural_direction: TrendDirection,
        evidence_direction: TrendDirection,
        ema_bullish: bool,
        ema_bearish: bool,
        momentum_bullish: bool,
        momentum_bearish: bool,
    ) -> TrendDirection:

        # Structural direction gets priority because
        # structure represents actual price behavior.

        if structural_direction == TrendDirection.BULLISH:

            if (
                evidence_direction
                == TrendDirection.BEARISH
                and ema_bearish
                and momentum_bearish
            ):
                return TrendDirection.SIDEWAYS

            return TrendDirection.BULLISH

        if structural_direction == TrendDirection.BEARISH:

            if (
                evidence_direction
                == TrendDirection.BULLISH
                and ema_bullish
                and momentum_bullish
            ):
                return TrendDirection.SIDEWAYS

            return TrendDirection.BEARISH

        # No reliable structure.
        # Fall back to evidence.

        if evidence_direction in (
            TrendDirection.BULLISH,
            TrendDirection.BEARISH,
        ):
            return evidence_direction

        if ema_bullish and momentum_bullish:
            return TrendDirection.BULLISH

        if ema_bearish and momentum_bearish:
            return TrendDirection.BEARISH

        return TrendDirection.SIDEWAYS

    # =========================================================================
    # AGREEMENT
    # =========================================================================

    @staticmethod
    def _calculate_agreement(
        direction: TrendDirection,
        structural_direction: TrendDirection,
        evidence_direction: TrendDirection,
        ema_bullish: bool,
        ema_bearish: bool,
        momentum_bullish: bool,
        momentum_bearish: bool,
    ) -> float:

        if direction == TrendDirection.SIDEWAYS:
            return 40.0

        score = 0.0

        if structural_direction == direction:
            score += 35.0

        if evidence_direction == direction:
            score += 25.0

        if direction == TrendDirection.BULLISH:

            if ema_bullish:
                score += 20.0

            if momentum_bullish:
                score += 20.0

        elif direction == TrendDirection.BEARISH:

            if ema_bearish:
                score += 20.0

            if momentum_bearish:
                score += 20.0

        return round(
            min(score, 100.0),
            2,
        )

    # =========================================================================
    # CONFIDENCE
    # =========================================================================

    @classmethod
    def _adjust_confidence(
        cls,
        confidence: float,
        agreement: float,
        direction: TrendDirection,
    ) -> float:

        confidence = float(confidence)

        if direction == TrendDirection.UNKNOWN:
            return 0.0

        # Agreement modifies, rather than replaces,
        # the underlying engine confidence.

        adjustment = (
            agreement - 60.0
        ) * 0.25

        confidence += adjustment

        if direction == TrendDirection.SIDEWAYS:
            confidence *= 0.75

        return round(
            cls._clamp(confidence),
            2,
        )

    # =========================================================================
    # STRENGTH
    # =========================================================================

    @classmethod
    def _calculate_strength(
        cls,
        confidence: float,
        momentum_confidence: float,
        structure_count: int,
        trendline_confidence: float,
        agreement: float,
    ) -> float:

        structure_quality = min(
            100.0,
            structure_count * 12.5,
        )

        strength = (
            confidence * 0.35
            + momentum_confidence * 0.25
            + structure_quality * 0.20
            + trendline_confidence * 0.10
            + agreement * 0.10
        )

        return round(
            cls._clamp(strength),
            2,
        )

    # =========================================================================
    # REASONS
    # =========================================================================

    @staticmethod
    def _build_reasons(
        direction: TrendDirection,
        structural_direction: TrendDirection,
        evidence_direction: TrendDirection,
        ema,
        momentum,
        trendline,
        agreement: float,
        confidence: float,
    ) -> list[str]:

        reasons: list[str] = []

        reasons.append(
            f"Final trend direction: "
            f"{direction.value}"
        )

        reasons.append(
            f"Structural direction: "
            f"{structural_direction.value}"
        )

        reasons.append(
            f"Indicator evidence direction: "
            f"{evidence_direction.value}"
        )

        reasons.append(
            f"EMA confidence: "
            f"{ema.confidence:.2f}"
        )

        reasons.append(
            f"Momentum confidence: "
            f"{momentum.confidence:.2f}"
        )

        reasons.append(
            f"Trendline confidence: "
            f"{trendline.confidence:.2f}"
        )

        reasons.append(
            f"Evidence agreement: "
            f"{agreement:.2f}"
        )

        reasons.append(
            f"Final confidence: "
            f"{confidence:.2f}"
        )

        if ema.bullish_alignment:
            reasons.append(
                "EMA stack is bullish."
            )

        elif ema.bearish_alignment:
            reasons.append(
                "EMA stack is bearish."
            )

        else:
            reasons.append(
                "EMA stack is not fully aligned."
            )

        if momentum.bullish:
            reasons.append(
                "Price momentum is bullish."
            )

        elif momentum.bearish:
            reasons.append(
                "Price momentum is bearish."
            )

        else:
            reasons.append(
                "Momentum is neutral."
            )

        if trendline.bullish_trendline:
            reasons.append(
                "Bullish trendline structure detected."
            )

        if trendline.bearish_trendline:
            reasons.append(
                "Bearish trendline structure detected."
            )

        return reasons

    # =========================================================================
    # CHART ANNOTATIONS
    # =========================================================================

    @staticmethod
    def _build_chart_annotations(
        context: MarketContext,
        swings,
        structures,
        trendline,
        ema,
        direction,
        confidence,
    ) -> list[dict]:

        annotations: list[dict] = []

        # ---------------------------------------------------------------------
        # Swing points
        # ---------------------------------------------------------------------

        for swing in swings:

            annotations.append(
                {
                    "type": "SWING",
                    "subtype": swing.swing_type.value,
                    "index": swing.index,
                    "price": swing.price,
                    "timestamp": swing.timestamp,
                    "locked": True,
                    "source": "trend",
                }
            )

        # ---------------------------------------------------------------------
        # Structure labels
        #
        # Dow structures correspond to the sequence after comparison.
        # They are linked to the latest available swing of the relevant type.
        # ---------------------------------------------------------------------

        for index, structure in enumerate(
            structures
        ):

            annotations.append(
                {
                    "type": "MARKET_STRUCTURE",
                    "subtype": structure.value,
                    "structure_index": index,
                    "locked": True,
                    "source": "trend",
                }
            )

        # ---------------------------------------------------------------------
        # Trendline
        # ---------------------------------------------------------------------

        if trendline.bullish_trendline:

            annotations.append(
                {
                    "type": "TRENDLINE",
                    "subtype": "BULLISH",
                    "slope": trendline.slope,
                    "touches": trendline.touches,
                    "confidence": trendline.confidence,
                    "locked": True,
                    "source": "trend",
                }
            )

        if trendline.bearish_trendline:

            annotations.append(
                {
                    "type": "TRENDLINE",
                    "subtype": "BEARISH",
                    "slope": trendline.slope,
                    "touches": trendline.touches,
                    "confidence": trendline.confidence,
                    "locked": True,
                    "source": "trend",
                }
            )

        # ---------------------------------------------------------------------
        # EMA regime
        # ---------------------------------------------------------------------

        annotations.append(
            {
                "type": "EMA_REGIME",
                "subtype": (
                    "BULLISH"
                    if ema.bullish_alignment
                    else (
                        "BEARISH"
                        if ema.bearish_alignment
                        else "MIXED"
                    )
                ),
                "ema20": ema.ema20,
                "ema50": ema.ema50,
                "ema100": ema.ema100,
                "ema200": ema.ema200,
                "confidence": ema.confidence,
                "locked": True,
                "source": "trend",
            }
        )

        # ---------------------------------------------------------------------
        # Final trend state
        # ---------------------------------------------------------------------

        annotations.append(
            {
                "type": "TREND_STATE",
                "subtype": direction.value,
                "symbol": context.symbol,
                "timeframe": context.timeframe,
                "confidence": confidence,
                "locked": True,
                "source": "trend",
            }
        )

        return annotations

    # =========================================================================
    # UTILITY
    # =========================================================================

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                float(value),
            ),
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

trend_engine = TrendEngine()
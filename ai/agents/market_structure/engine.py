"""
===============================================================================
COSMOS Market Structure Engine

Main orchestration engine for institutional market structure analysis.

Pipeline:

    Trend Shared Memory
        ↓
    Raw Structure (HH / HL / LH / LL)
        ↓
    BOS Detection
        ↓
    CHOCH Detection
        ↓
    Internal Structure
        ↓
    External Structure
        ↓
    Confidence
        ↓
    Market Structure Analysis
        ↓
    Shared Memory
        ↓
    Agent Result

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.context import MarketContext
from ai.models import AgentResult

from ai.agents.market_structure.structure_engine import (
    StructureEngine,
)

from ai.agents.market_structure.bos_engine import (
    BOSEngine,
)

from ai.agents.market_structure.choch_engine import (
    CHOCHEngine,
)

from ai.agents.market_structure.internal_engine import (
    InternalStructureEngine,
)

from ai.agents.market_structure.external_engine import (
    ExternalStructureEngine,
)

from ai.agents.market_structure.confidence_engine import (
    ConfidenceEngine,
)

from ai.agents.market_structure.models import (
    MarketStructureAnalysis,
    StructureBias,
)


class MarketStructureEngine:
    """
    Main institutional Market Structure Agent.

    Consumes swing information from Trend Agent shared memory
    and produces:

        - raw HH / HL / LH / LL structure
        - BOS
        - CHOCH
        - internal structure
        - external structure
        - confidence
        - final market structure analysis

    The complete output is published to:

        context.memory["market_structure"]

    and:

        context.results["market_structure"]
    """

    AGENT_NAME = "market_structure"
    AGENT_VERSION = "1.0.0"

    def __init__(self) -> None:

        # -------------------------------------------------------------
        # Raw structure
        # -------------------------------------------------------------

        self.structure_engine = (
            StructureEngine()
        )

        # -------------------------------------------------------------
        # BOS
        # -------------------------------------------------------------

        self.bos_engine = (
            BOSEngine()
        )

        # -------------------------------------------------------------
        # CHOCH
        # -------------------------------------------------------------

        self.choch_engine = (
            CHOCHEngine()
        )

        # -------------------------------------------------------------
        # Internal structure
        # -------------------------------------------------------------

        self.internal_engine = (
            InternalStructureEngine()
        )

        # -------------------------------------------------------------
        # External structure
        # -------------------------------------------------------------

        self.external_engine = (
            ExternalStructureEngine()
        )

        # -------------------------------------------------------------
        # Confidence
        # -------------------------------------------------------------

        self.confidence_engine = (
            ConfidenceEngine()
        )

    # =================================================================
    # MAIN ANALYSIS
    # =================================================================

    def analyze(
        self,
        context: MarketContext,
    ) -> AgentResult:
        """
        Run the complete Market Structure pipeline.
        """

        # =============================================================
        # 1. VALIDATION
        # =============================================================

        if context is None:

            raise ValueError(
                "MarketContext cannot be None."
            )

        if not context.candles:

            raise ValueError(
                "Candles are required."
            )

        if not hasattr(
            context,
            "memory",
        ):

            raise AttributeError(
                "MarketContext.memory is required."
            )

        # =============================================================
        # 2. TREND SHARED MEMORY
        # =============================================================

        trend_memory = context.memory.get(
            "trend"
        )

        if trend_memory is None:

            raise RuntimeError(
                "Trend Agent must run first."
            )

        # =============================================================
        # 3. SWINGS
        # =============================================================

        swings = trend_memory.get(
            "swings",
            [],
        )

        if not swings:

            raise RuntimeError(
                "Trend Agent did not provide swing data."
            )

        # =============================================================
        # 4. RAW MARKET STRUCTURE
        # =============================================================
        #
        # HH / HL / LH / LL
        #
        # This is intentionally kept separate from BOS / CHOCH.
        # =============================================================

        structure = (
            self.structure_engine.analyze(
                swings
            )
        )

        # =============================================================
        # 5. BOS
        # =============================================================

        bos = (
            self.bos_engine.analyze(
                swings
            )
        )

        # =============================================================
        # 6. CHOCH
        # =============================================================

        choch = (
            self.choch_engine.analyze(
                swings
            )
        )

        # =============================================================
        # 7. INTERNAL STRUCTURE
        # =============================================================

        internal = (
            self.internal_engine.analyze(

                bullish_bos=(
                    bos.bullish
                ),

                bearish_bos=(
                    bos.bearish
                ),

                bullish_choch=(
                    choch.bullish
                ),

                bearish_choch=(
                    choch.bearish
                ),
            )
        )

        # =============================================================
        # 8. EXTERNAL STRUCTURE
        # =============================================================

        bullish_count = 0
        bearish_count = 0

        if bos.bullish:

            bullish_count += 1

        if choch.bullish:

            bullish_count += 1

        if bos.bearish:

            bearish_count += 1

        if choch.bearish:

            bearish_count += 1

        external = (
            self.external_engine.analyze(

                bullish_count=(
                    bullish_count
                ),

                bearish_count=(
                    bearish_count
                ),
            )
        )

        # =============================================================
        # 9. CONFIDENCE
        # =============================================================

        confidence = (
            self.confidence_engine.calculate(

                bos=bos,

                choch=choch,

                internal=internal,

                external=external,
            )
        )

        confidence = max(
            0.0,
            min(
                100.0,
                float(confidence),
            ),
        )

        # =============================================================
        # 10. FINAL BIAS
        # =============================================================

        if (
            internal.bias
            == StructureBias.BULLISH
        ):

            bias = (
                StructureBias.BULLISH
            )

        elif (
            internal.bias
            == StructureBias.BEARISH
        ):

            bias = (
                StructureBias.BEARISH
            )

        elif (
            external.bias
            == StructureBias.BULLISH
        ):

            bias = (
                StructureBias.BULLISH
            )

        elif (
            external.bias
            == StructureBias.BEARISH
        ):

            bias = (
                StructureBias.BEARISH
            )

        else:

            bias = (
                StructureBias.NEUTRAL
            )

        # =============================================================
        # 11. CHOCH / MSS FLAGS
        # =============================================================

        choch_detected = bool(
            choch.bullish
            or choch.bearish
        )

        mss_detected = bool(
            choch_detected
        )

        # =============================================================
        # 12. REASONS
        # =============================================================

        reasons: list[str] = []

        reasons.append(
            f"Higher Highs: "
            f"{structure.higher_highs}"
        )

        reasons.append(
            f"Higher Lows: "
            f"{structure.higher_lows}"
        )

        reasons.append(
            f"Lower Highs: "
            f"{structure.lower_highs}"
        )

        reasons.append(
            f"Lower Lows: "
            f"{structure.lower_lows}"
        )

        reasons.append(
            f"Structure Bias: "
            f"{structure.bias.value}"
        )

        reasons.append(
            f"BOS Bullish: "
            f"{bos.bullish}"
        )

        reasons.append(
            f"BOS Bearish: "
            f"{bos.bearish}"
        )

        reasons.append(
            f"CHOCH Bullish: "
            f"{choch.bullish}"
        )

        reasons.append(
            f"CHOCH Bearish: "
            f"{choch.bearish}"
        )

        reasons.append(
            f"Internal Bias: "
            f"{internal.bias.value}"
        )

        reasons.append(
            f"External Bias: "
            f"{external.bias.value}"
        )

        reasons.append(
            f"Final Bias: "
            f"{bias.value}"
        )

        reasons.append(
            f"Confidence: "
            f"{confidence:.2f}"
        )

        # =============================================================
        # 13. FINAL ANALYSIS
        # =============================================================

        analysis = MarketStructureAnalysis(

            bullish_bos=bool(
                bos.bullish
            ),

            bearish_bos=bool(
                bos.bearish
            ),

            choch=(
                choch_detected
            ),

            mss=(
                mss_detected
            ),

            internal_bias=(
                internal.bias
            ),

            external_bias=(
                external.bias
            ),

            confidence=round(
                confidence,
                2,
            ),

            reasons=reasons,
        )

        # =============================================================
        # 14. AGENT RESULT
        # =============================================================

        result = AgentResult(

            name=self.AGENT_NAME,

            confidence=round(
                confidence,
                2,
            ),

            success=True,

            analysis=analysis,
        )

        # =============================================================
        # 15. SHARED MEMORY
        # =============================================================
        #
        # IMPORTANT:
        #
        # LiquidityEngine expects:
        #
        #     memory["market_structure"]["swings"]
        #
        # Therefore raw swings MUST remain here.
        #
        # We also expose the raw StructureEngine result separately.
        # =============================================================

        context.memory[
            "market_structure"
        ] = {

            # ---------------------------------------------------------
            # Raw swing data
            # ---------------------------------------------------------

            "swings": swings,

            # ---------------------------------------------------------
            # HH / HL / LH / LL structure
            # ---------------------------------------------------------

            "structure": structure,

            # ---------------------------------------------------------
            # Final analysis
            # ---------------------------------------------------------

            "analysis": analysis,

            # ---------------------------------------------------------
            # Final bias
            # ---------------------------------------------------------

            "bias": bias,

            # ---------------------------------------------------------
            # BOS
            # ---------------------------------------------------------

            "bullish_bos": (
                bool(
                    bos.bullish
                )
            ),

            "bearish_bos": (
                bool(
                    bos.bearish
                )
            ),

            "bos": bos,

            # ---------------------------------------------------------
            # CHOCH
            # ---------------------------------------------------------

            "choch": (
                choch_detected
            ),

            "choch_analysis": choch,

            # ---------------------------------------------------------
            # MSS
            # ---------------------------------------------------------

            "mss": (
                mss_detected
            ),

            # ---------------------------------------------------------
            # Internal / External
            # ---------------------------------------------------------

            "internal": internal,

            "external": external,

            # ---------------------------------------------------------
            # Confidence
            # ---------------------------------------------------------

            "confidence": confidence,

            # ---------------------------------------------------------
            # Reasons
            # ---------------------------------------------------------

            "reasons": reasons,

            # ---------------------------------------------------------
            # Agent result
            # ---------------------------------------------------------

            "result": result,
        }

        # =============================================================
        # 16. STORE RESULT
        # =============================================================

        context.add_result(
            result
        )

        return result


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

market_structure_engine = (
    MarketStructureEngine()
)
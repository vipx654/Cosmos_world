"""
===============================================================================
COSMOS External Structure Engine

Analyzes the dominant market structure.

Responsibilities:

    - External bullish structure
    - External bearish structure
    - Dominant structural direction
    - Structural strength
    - Structural confidence
    - Safe count handling

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.agents.market_structure.models import (
    StructureBias,
)


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class ExternalStructureAnalysis:
    """
    Dominant external market structure.
    """

    bias: StructureBias

    strength: float

    confidence: float


# =============================================================================
# ENGINE
# =============================================================================


class ExternalStructureEngine:
    """
    Determines the dominant external market structure.

    External structure represents the larger structural
    direction rather than short-term internal movement.

    The engine compares bullish and bearish structural
    evidence and assigns the dominant direction.
    """

    def analyze(
        self,
        bullish_count: int,
        bearish_count: int,
    ) -> ExternalStructureAnalysis:

        # =====================================================================
        # 1. NORMALIZE INPUT
        # =====================================================================

        bullish_count = max(

            0,

            int(bullish_count),

        )

        bearish_count = max(

            0,

            int(bearish_count),

        )

        # =====================================================================
        # 2. TOTAL STRUCTURAL EVIDENCE
        # =====================================================================

        total = (

            bullish_count

            + bearish_count

        )

        # =====================================================================
        # 3. NO STRUCTURAL EVIDENCE
        # =====================================================================

        if total == 0:

            return ExternalStructureAnalysis(

                bias=StructureBias.NEUTRAL,

                strength=0.0,

                confidence=0.0,

            )

        # =====================================================================
        # 4. BULLISH DOMINANCE
        # =====================================================================

        if bullish_count > bearish_count:

            bias = StructureBias.BULLISH

            strength = (

                bullish_count

                / total

            ) * 100.0

        # =====================================================================
        # 5. BEARISH DOMINANCE
        # =====================================================================

        elif bearish_count > bullish_count:

            bias = StructureBias.BEARISH

            strength = (

                bearish_count

                / total

            ) * 100.0

        # =====================================================================
        # 6. STRUCTURAL CONFLICT
        # =====================================================================

        else:

            bias = StructureBias.NEUTRAL

            strength = 0.0

        # =====================================================================
        # 7. CONFIDENCE
        # =====================================================================

        confidence = strength

        # =====================================================================
        # 8. FINAL BOUNDS
        # =====================================================================

        strength = max(

            0.0,

            min(

                100.0,

                float(strength),

            ),

        )

        confidence = max(

            0.0,

            min(

                100.0,

                float(confidence),

            ),

        )

        # =====================================================================
        # 9. RESULT
        # =====================================================================

        return ExternalStructureAnalysis(

            bias=bias,

            strength=round(

                strength,

                2,

            ),

            confidence=round(

                confidence,

                2,

            ),

        )
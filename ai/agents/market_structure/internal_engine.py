"""
===============================================================================
COSMOS Internal Structure Engine

Analyzes the internal market structure.

Responsibilities:

    - Internal bullish structure
    - Internal bearish structure
    - BOS / CHOCH contribution
    - Structural strength
    - Structural confidence
    - Direction conflict handling

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
class InternalStructureAnalysis:
    """
    Internal market structure result.
    """

    bias: StructureBias

    strength: float

    confidence: float


# =============================================================================
# ENGINE
# =============================================================================


class InternalStructureEngine:
    """
    Determines the internal market structure bias.

    BOS provides the primary structural direction.

    CHOCH provides additional confirmation that
    internal structure is changing.

    If both bullish and bearish structural signals
    are present, the engine resolves the conflict
    conservatively.
    """

    def analyze(
        self,
        bullish_bos: bool,
        bearish_bos: bool,
        bullish_choch: bool,
        bearish_choch: bool,
    ) -> InternalStructureAnalysis:

        # =====================================================================
        # 1. INITIAL STATE
        # =====================================================================

        bullish_strength = 0.0

        bearish_strength = 0.0

        bullish_confidence = 0.0

        bearish_confidence = 0.0

        # =====================================================================
        # 2. BULLISH BOS
        # =====================================================================

        if bullish_bos:

            bullish_strength += 60.0

            bullish_confidence += 60.0

        # =====================================================================
        # 3. BULLISH CHOCH
        # =====================================================================

        if bullish_choch:

            bullish_strength += 20.0

            bullish_confidence += 15.0

        # =====================================================================
        # 4. BEARISH BOS
        # =====================================================================

        if bearish_bos:

            bearish_strength += 60.0

            bearish_confidence += 60.0

        # =====================================================================
        # 5. BEARISH CHOCH
        # =====================================================================

        if bearish_choch:

            bearish_strength += 20.0

            bearish_confidence += 15.0

        # =====================================================================
        # 6. BOUNDS
        # =====================================================================

        bullish_strength = min(

            bullish_strength,

            100.0,

        )

        bearish_strength = min(

            bearish_strength,

            100.0,

        )

        bullish_confidence = min(

            bullish_confidence,

            100.0,

        )

        bearish_confidence = min(

            bearish_confidence,

            100.0,

        )

        # =====================================================================
        # 7. BIAS RESOLUTION
        # =====================================================================

        bias = StructureBias.NEUTRAL

        strength = 0.0

        confidence = 0.0

        # ---------------------------------------------------------------------
        # Bullish dominance
        # ---------------------------------------------------------------------

        if (

            bullish_strength > bearish_strength

        ):

            bias = StructureBias.BULLISH

            strength = bullish_strength

            confidence = bullish_confidence

        # ---------------------------------------------------------------------
        # Bearish dominance
        # ---------------------------------------------------------------------

        elif (

            bearish_strength > bullish_strength

        ):

            bias = StructureBias.BEARISH

            strength = bearish_strength

            confidence = bearish_confidence

        # ---------------------------------------------------------------------
        # Conflict / equal structure
        # ---------------------------------------------------------------------

        else:

            bias = StructureBias.NEUTRAL

            strength = 0.0

            confidence = 0.0

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

        return InternalStructureAnalysis(

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
"""
===============================================================================
COSMOS Internal Structure Engine

Analyzes the internal market structure.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.agents.market_structure.models import StructureBias


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class InternalStructureAnalysis:
    """
    Internal market structure.
    """

    bias: StructureBias

    strength: float

    confidence: float


# =============================================================================
# ENGINE
# =============================================================================


class InternalStructureEngine:
    """
    Determines the internal structure bias using
    BOS and CHOCH.
    """

    def analyze(
        self,
        bullish_bos: bool,
        bearish_bos: bool,
        bullish_choch: bool,
        bearish_choch: bool,
    ) -> InternalStructureAnalysis:

        bias = StructureBias.NEUTRAL

        strength = 0.0

        confidence = 0.0

        # ---------------------------------------------------------
        # Bullish Internal Structure
        # ---------------------------------------------------------

        if bullish_bos:

            bias = StructureBias.BULLISH

            strength += 60

            confidence += 60

        if bullish_choch:

            strength += 20

            confidence += 15

        # ---------------------------------------------------------
        # Bearish Internal Structure
        # ---------------------------------------------------------

        if bearish_bos:

            bias = StructureBias.BEARISH

            strength += 60

            confidence += 60

        if bearish_choch:

            strength += 20

            confidence += 15

        strength = min(strength, 100.0)

        confidence = min(confidence, 100.0)

        return InternalStructureAnalysis(

            bias=bias,

            strength=strength,

            confidence=confidence,
        )
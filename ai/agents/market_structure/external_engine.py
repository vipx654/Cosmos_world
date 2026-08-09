"""
===============================================================================
COSMOS External Structure Engine

Analyzes the dominant market structure.

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
class ExternalStructureAnalysis:
    """
    Dominant market structure.
    """

    bias: StructureBias

    strength: float

    confidence: float


# =============================================================================
# ENGINE
# =============================================================================


class ExternalStructureEngine:
    """
    Determines the dominant market structure.

    Unlike Internal Structure, this engine focuses
    on the major trend.
    """

    def analyze(
        self,
        bullish_count: int,
        bearish_count: int,
    ) -> ExternalStructureAnalysis:

        bias = StructureBias.NEUTRAL

        strength = 0.0

        confidence = 0.0

        total = bullish_count + bearish_count

        if total == 0:

            return ExternalStructureAnalysis(
                bias=bias,
                strength=0.0,
                confidence=0.0,
            )

        if bullish_count > bearish_count:

            bias = StructureBias.BULLISH

            strength = (
                bullish_count / total
            ) * 100

        elif bearish_count > bullish_count:

            bias = StructureBias.BEARISH

            strength = (
                bearish_count / total
            ) * 100

        confidence = strength

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
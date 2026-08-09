"""
===============================================================================
COSMOS Market Structure Confidence Engine

Combines all market structure engines into one institutional confidence score.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.market_structure.bos_engine import BOSAnalysis
from ai.agents.market_structure.choch_engine import CHOCHAnalysis
from ai.agents.market_structure.internal_engine import (
    InternalStructureAnalysis,
)
from ai.agents.market_structure.external_engine import (
    ExternalStructureAnalysis,
)


class ConfidenceEngine:
    """
    Calculates the overall confidence of the
    Market Structure Agent.
    """

    def calculate(
        self,
        bos: BOSAnalysis,
        choch: CHOCHAnalysis,
        internal: InternalStructureAnalysis,
        external: ExternalStructureAnalysis,
    ) -> float:

        score = 0.0

        # ---------------------------------------------------------
        # BOS
        # ---------------------------------------------------------

        score += bos.confidence * 0.35

        # ---------------------------------------------------------
        # CHOCH
        # ---------------------------------------------------------

        score += choch.confidence * 0.20

        # ---------------------------------------------------------
        # Internal Structure
        # ---------------------------------------------------------

        score += internal.confidence * 0.20

        # ---------------------------------------------------------
        # External Structure
        # ---------------------------------------------------------

        score += external.confidence * 0.25

        return round(
            min(score, 100.0),
            2,
        )
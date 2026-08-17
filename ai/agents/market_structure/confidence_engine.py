"""
===============================================================================
COSMOS Market Structure Confidence Engine

Combines BOS, CHOCH, MSS, Internal Structure and External Structure
into one bounded institutional confidence score.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.market_structure.bos_engine import (
    BOSAnalysis,
)

from ai.agents.market_structure.choch_engine import (
    CHOCHAnalysis,
)

from ai.agents.market_structure.internal_engine import (
    InternalStructureAnalysis,
)

from ai.agents.market_structure.external_engine import (
    ExternalStructureAnalysis,
)


# =============================================================================
# WEIGHTS
# =============================================================================

WEIGHT_BOS = 0.35

WEIGHT_CHOCH = 0.20

WEIGHT_MSS = 0.00

WEIGHT_INTERNAL = 0.20

WEIGHT_EXTERNAL = 0.25


# =============================================================================
# ENGINE
# =============================================================================


class ConfidenceEngine:
    """
    Calculates the overall confidence of the
    Market Structure Agent.

    Current compatibility pipeline:

        BOS       -> 35%
        CHOCH     -> 20%
        MSS       -> optional / 0% until fully integrated
        Internal  -> 20%
        External  -> 25%

    The final confidence is always bounded
    between 0 and 100.

    MSS is intentionally optional here because the current
    MarketStructureEngine calls calculate() with:

        bos
        choch
        internal
        external

    This preserves compatibility with the existing pipeline
    while allowing MSS to be integrated later without another
    breaking change.
    """

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def _bounded_confidence(
        value: float,
    ) -> float:
        """
        Normalize an individual confidence value
        into the valid 0-100 range.
        """

        return max(
            0.0,
            min(
                100.0,
                float(value),
            ),
        )

    # =========================================================================
    # MAIN CALCULATION
    # =========================================================================

    def calculate(
        self,
        bos: BOSAnalysis,
        choch: CHOCHAnalysis,
        internal: InternalStructureAnalysis,
        external: ExternalStructureAnalysis,
        mss=None,
    ) -> float:
        """
        Calculate the weighted Market Structure
        confidence score.

        Parameters
        ----------
        bos:
            BOS analysis result.

        choch:
            CHOCH analysis result.

        internal:
            Internal structure result.

        external:
            External structure result.

        mss:
            Optional MSS analysis result.

            Kept optional for backwards compatibility with
            the current MarketStructureEngine.
        """

        # =====================================================================
        # 1. EXTRACT BOS CONFIDENCE
        # =====================================================================

        bos_confidence = self._bounded_confidence(
            bos.confidence
        )

        # =====================================================================
        # 2. EXTRACT CHOCH CONFIDENCE
        # =====================================================================

        choch_confidence = self._bounded_confidence(
            choch.confidence
        )

        # =====================================================================
        # 3. EXTRACT INTERNAL CONFIDENCE
        # =====================================================================

        internal_confidence = self._bounded_confidence(
            internal.confidence
        )

        # =====================================================================
        # 4. EXTRACT EXTERNAL CONFIDENCE
        # =====================================================================

        external_confidence = self._bounded_confidence(
            external.confidence
        )

        # =====================================================================
        # 5. OPTIONAL MSS CONFIDENCE
        # =====================================================================

        mss_confidence = 0.0

        if mss is not None:

            mss_confidence = self._bounded_confidence(
                getattr(
                    mss,
                    "confidence",
                    0.0,
                )
            )

        # =====================================================================
        # 6. WEIGHTED SCORE
        # =====================================================================

        score = 0.0

        score += (
            bos_confidence
            * WEIGHT_BOS
        )

        score += (
            choch_confidence
            * WEIGHT_CHOCH
        )

        score += (
            mss_confidence
            * WEIGHT_MSS
        )

        score += (
            internal_confidence
            * WEIGHT_INTERNAL
        )

        score += (
            external_confidence
            * WEIGHT_EXTERNAL
        )

        # =====================================================================
        # 7. FINAL BOUNDS
        # =====================================================================

        score = max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

        # =====================================================================
        # 8. RESULT
        # =====================================================================

        return round(
            score,
            2,
        )
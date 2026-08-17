"""
===============================================================================
COSMOS Structure Engine

Detects institutional market structure.

Responsibilities:

    - Higher Highs
    - Higher Lows
    - Lower Highs
    - Lower Lows
    - Structure Bias
    - Protected High
    - Protected Low
    - Structure Strength
    - Structure Confidence

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.market_structure.models import (
    StructureBias,
    StructureLevel,
    StructureLevelType,
)


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class StructureAnalysis:
    """
    Raw institutional market structure analysis.

    This result is intentionally independent from
    BOS and CHOCH detection.
    """

    higher_highs: int

    higher_lows: int

    lower_highs: int

    lower_lows: int

    bias: StructureBias

    protected_high: StructureLevel | None = None

    protected_low: StructureLevel | None = None

    strength: float = 0.0

    confidence: float = 0.0


# =============================================================================
# ENGINE
# =============================================================================


class StructureEngine:
    """
    Reads swing points and determines the current
    institutional market structure.

    The engine evaluates:

        HH / HL
        LH / LL
        dominant bias
        protected structural levels
        structure strength
        structure confidence
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> StructureAnalysis:

        # =====================================================================
        # 1. EMPTY INPUT
        # =====================================================================

        if not swings:

            return StructureAnalysis(

                higher_highs=0,

                higher_lows=0,

                lower_highs=0,

                lower_lows=0,

                bias=StructureBias.NEUTRAL,

                protected_high=None,

                protected_low=None,

                strength=0.0,

                confidence=0.0,
            )

        # =====================================================================
        # 2. SEPARATE SWINGS
        # =====================================================================

        highs = [

            swing

            for swing in swings

            if swing.swing_type == SwingType.HIGH

        ]

        lows = [

            swing

            for swing in swings

            if swing.swing_type == SwingType.LOW

        ]

        # =====================================================================
        # 3. HH / HL / LH / LL
        # =====================================================================

        higher_highs = 0

        higher_lows = 0

        lower_highs = 0

        lower_lows = 0

        previous_high: float | None = None

        previous_low: float | None = None

        for swing in swings:

            # -----------------------------------------------------------------
            # HIGH
            # -----------------------------------------------------------------

            if swing.swing_type == SwingType.HIGH:

                if previous_high is not None:

                    if swing.price > previous_high:

                        higher_highs += 1

                    elif swing.price < previous_high:

                        lower_highs += 1

                previous_high = swing.price

            # -----------------------------------------------------------------
            # LOW
            # -----------------------------------------------------------------

            elif swing.swing_type == SwingType.LOW:

                if previous_low is not None:

                    if swing.price > previous_low:

                        higher_lows += 1

                    elif swing.price < previous_low:

                        lower_lows += 1

                previous_low = swing.price

        # =====================================================================
        # 4. STRUCTURE BIAS
        # =====================================================================

        bullish_score = (

            higher_highs

            + higher_lows

        )

        bearish_score = (

            lower_highs

            + lower_lows

        )

        bias = StructureBias.NEUTRAL

        if (

            bullish_score > bearish_score

            and bullish_score > 0

        ):

            bias = StructureBias.BULLISH

        elif (

            bearish_score > bullish_score

            and bearish_score > 0

        ):

            bias = StructureBias.BEARISH

        # =====================================================================
        # 5. PROTECTED HIGH / LOW
        # =====================================================================

        protected_high = self._find_protected_high(

            swings=swings,

            bias=bias,

        )

        protected_low = self._find_protected_low(

            swings=swings,

            bias=bias,

        )

        # =====================================================================
        # 6. STRUCTURE STRENGTH
        # =====================================================================

        total_structure_events = (

            bullish_score

            + bearish_score

        )

        if total_structure_events == 0:

            strength = 0.0

        else:

            dominant_score = max(

                bullish_score,

                bearish_score,

            )

            strength = (

                dominant_score

                / total_structure_events

            ) * 100.0

        strength = max(

            0.0,

            min(

                100.0,

                strength,

            ),

        )

        # =====================================================================
        # 7. STRUCTURE CONFIDENCE
        # =====================================================================

        confidence = self._calculate_confidence(

            higher_highs=higher_highs,

            higher_lows=higher_lows,

            lower_highs=lower_highs,

            lower_lows=lower_lows,

            bias=bias,

        )

        # =====================================================================
        # 8. FINAL RESULT
        # =====================================================================

        return StructureAnalysis(

            higher_highs=higher_highs,

            higher_lows=higher_lows,

            lower_highs=lower_highs,

            lower_lows=lower_lows,

            bias=bias,

            protected_high=protected_high,

            protected_low=protected_low,

            strength=round(

                strength,

                2,

            ),

            confidence=round(

                confidence,

                2,

            ),

        )

    # =========================================================================
    # PROTECTED HIGH
    # =========================================================================

    def _find_protected_high(

        self,

        swings: list[SwingPoint],

        bias: StructureBias,

    ) -> StructureLevel | None:

        highs = [

            swing

            for swing in swings

            if swing.swing_type == SwingType.HIGH

        ]

        if not highs:

            return None

        # ---------------------------------------------------------------------
        # Bullish structure
        #
        # The latest structural high becomes the current
        # protected high until price breaks it.
        # ---------------------------------------------------------------------

        if bias == StructureBias.BULLISH:

            swing = highs[-1]

        # ---------------------------------------------------------------------
        # Bearish / neutral structure
        #
        # Use the latest available structural high.
        # ---------------------------------------------------------------------

        else:

            swing = highs[-1]

        return StructureLevel(

            level_type=StructureLevelType.HIGH,

            price=swing.price,

            index=swing.index,

        )

    # =========================================================================
    # PROTECTED LOW
    # =========================================================================

    def _find_protected_low(

        self,

        swings: list[SwingPoint],

        bias: StructureBias,

    ) -> StructureLevel | None:

        lows = [

            swing

            for swing in swings

            if swing.swing_type == SwingType.LOW

        ]

        if not lows:

            return None

        # ---------------------------------------------------------------------
        # Bearish structure
        #
        # The latest structural low becomes the current
        # protected low until price breaks it.
        # ---------------------------------------------------------------------

        if bias == StructureBias.BEARISH:

            swing = lows[-1]

        # ---------------------------------------------------------------------
        # Bullish / neutral structure
        #
        # Use the latest available structural low.
        # ---------------------------------------------------------------------

        else:

            swing = lows[-1]

        return StructureLevel(

            level_type=StructureLevelType.LOW,

            price=swing.price,

            index=swing.index,

        )

    # =========================================================================
    # CONFIDENCE
    # =========================================================================

    def _calculate_confidence(

        self,

        higher_highs: int,

        higher_lows: int,

        lower_highs: int,

        lower_lows: int,

        bias: StructureBias,

    ) -> float:

        total_events = (

            higher_highs

            + higher_lows

            + lower_highs

            + lower_lows

        )

        if total_events == 0:

            return 0.0

        if bias == StructureBias.BULLISH:

            dominant = (

                higher_highs

                + higher_lows

            )

        elif bias == StructureBias.BEARISH:

            dominant = (

                lower_highs

                + lower_lows

            )

        else:

            dominant = max(

                higher_highs + higher_lows,

                lower_highs + lower_lows,

            )

        confidence = (

            dominant

            / total_events

        ) * 100.0

        return max(

            0.0,

            min(

                100.0,

                confidence,

            ),

        )
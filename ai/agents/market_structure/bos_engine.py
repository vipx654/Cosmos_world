"""
===============================================================================
COSMOS BOS Engine

Break Of Structure Detection

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.market_structure.constants import (
    MIN_BOS_DISTANCE,
)


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class BOSAnalysis:
    """
    Break Of Structure result.
    """

    bullish: bool

    bearish: bool

    broken_price: float | None

    confidence: float

    strength: float = 0.0

    distance: float = 0.0

    broken_index: int | None = None


# =============================================================================
# ENGINE
# =============================================================================


class BOSEngine:
    """
    Detects institutional Break Of Structure.

    Bullish BOS:
        Latest structural high breaks above
        the previous structural high.

    Bearish BOS:
        Latest structural low breaks below
        the previous structural low.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> BOSAnalysis:

        # =====================================================================
        # 1. VALIDATION
        # =====================================================================

        if len(swings) < 4:

            return BOSAnalysis(

                bullish=False,

                bearish=False,

                broken_price=None,

                confidence=0.0,

                strength=0.0,

                distance=0.0,

                broken_index=None,
            )

        # =====================================================================
        # 2. EXTRACT SWINGS
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

        bullish = False

        bearish = False

        broken_price = None

        broken_index = None

        confidence = 0.0

        strength = 0.0

        distance = 0.0

        # =====================================================================
        # 3. BULLISH BOS
        # =====================================================================

        if len(highs) >= 2:

            previous_high = highs[-2]

            current_high = highs[-1]

            index_distance = abs(

                current_high.index

                - previous_high.index

            )

            price_distance = (

                current_high.price

                - previous_high.price

            )

            if (

                current_high.price

                > previous_high.price

                and index_distance

                >= MIN_BOS_DISTANCE

            ):

                bullish = True

                broken_price = previous_high.price

                broken_index = current_high.index

                distance = abs(

                    price_distance

                )

                strength = 100.0

                confidence = 85.0

        # =====================================================================
        # 4. BEARISH BOS
        # =====================================================================

        if len(lows) >= 2:

            previous_low = lows[-2]

            current_low = lows[-1]

            index_distance = abs(

                current_low.index

                - previous_low.index

            )

            price_distance = (

                previous_low.price

                - current_low.price

            )

            if (

                current_low.price

                < previous_low.price

                and index_distance

                >= MIN_BOS_DISTANCE

            ):

                bearish = True

                broken_price = previous_low.price

                broken_index = current_low.index

                distance = abs(

                    price_distance

                )

                strength = 100.0

                confidence = max(

                    confidence,

                    85.0,

                )

        # =====================================================================
        # 5. BOUNDS
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
        # 6. RESULT
        # =====================================================================

        return BOSAnalysis(

            bullish=bool(

                bullish

            ),

            bearish=bool(

                bearish

            ),

            broken_price=broken_price,

            confidence=round(

                confidence,

                2,

            ),

            strength=round(

                strength,

                2,

            ),

            distance=round(

                distance,

                10,

            ),

            broken_index=broken_index,

        )
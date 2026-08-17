"""
===============================================================================
COSMOS CHOCH Engine

Change Of Character Detection

Responsibilities:

    - Bullish CHOCH detection
    - Bearish CHOCH detection
    - Structural break price
    - Structural distance
    - CHOCH strength
    - CHOCH confidence

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.market_structure.constants import (
    MIN_CHOCH_DISTANCE,
)


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class CHOCHAnalysis:
    """
    Change Of Character result.

    Existing fields are preserved for
    backward compatibility.
    """

    detected: bool

    bullish: bool

    bearish: bool

    confidence: float

    strength: float = 0.0

    broken_price: float | None = None

    distance: float = 0.0

    broken_index: int | None = None


# =============================================================================
# ENGINE
# =============================================================================


class CHOCHEngine:
    """
    Detects Change Of Character.

    Bullish CHOCH:

        A previous lower-high structure is broken
        by a higher structural high.

    Bearish CHOCH:

        A previous higher-low structure is broken
        by a lower structural low.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> CHOCHAnalysis:

        # =====================================================================
        # 1. VALIDATION
        # =====================================================================

        if len(swings) < 6:

            return CHOCHAnalysis(

                detected=False,

                bullish=False,

                bearish=False,

                confidence=0.0,

                strength=0.0,

                broken_price=None,

                distance=0.0,

                broken_index=None,
            )

        # =====================================================================
        # 2. EXTRACT STRUCTURAL SWINGS
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

        broken_price: float | None = None

        broken_index: int | None = None

        confidence = 0.0

        strength = 0.0

        distance = 0.0

        # =====================================================================
        # 3. BULLISH CHOCH
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

                >= MIN_CHOCH_DISTANCE

            ):

                bullish = True

                broken_price = previous_high.price

                broken_index = current_high.index

                distance = abs(

                    price_distance

                )

                strength = 100.0

                confidence = 75.0

        # =====================================================================
        # 4. BEARISH CHOCH
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

                >= MIN_CHOCH_DISTANCE

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

                    75.0,

                )

        # =====================================================================
        # 5. DETECTION
        # =====================================================================

        detected = (

            bullish

            or bearish

        )

        # =====================================================================
        # 6. BOUNDS
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
        # 7. RESULT
        # =====================================================================

        return CHOCHAnalysis(

            detected=bool(

                detected

            ),

            bullish=bool(

                bullish

            ),

            bearish=bool(

                bearish

            ),

            confidence=round(

                confidence,

                2,

            ),

            strength=round(

                strength,

                2,

            ),

            broken_price=broken_price,

            distance=round(

                distance,

                10,

            ),

            broken_index=broken_index,

        )
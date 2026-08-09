"""
===============================================================================
COSMOS Inducement Engine

Institutional Inducement Detection.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.smc.constants import (
    MIN_INDUCEMENT_DISTANCE,
)

from ai.agents.smc.models import (
    Inducement,
    InducementType,
)


class InducementEngine:
    """
    Detects institutional inducement.

    Inducement is a liquidity attraction move
    before the real expansion.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> Inducement:

        if len(swings) < 4:

            return Inducement(

                inducement_type=InducementType.NONE,

                price=0.0,

                confidence=0.0,
            )

        highs = [

            s

            for s in swings

            if s.swing_type == SwingType.HIGH

        ]

        lows = [

            s

            for s in swings

            if s.swing_type == SwingType.LOW

        ]

        # ---------------------------------------------------------
        # Buy Side Inducement
        # ---------------------------------------------------------

        if len(highs) >= 2:

            previous = highs[-2]

            current = highs[-1]

            distance = (

                current.price
                -
                previous.price

            )

            if (

                distance > 0

                and

                distance <= MIN_INDUCEMENT_DISTANCE

            ):

                return Inducement(

                    inducement_type=InducementType.BUY_SIDE,

                    price=current.price,

                    confidence=75.0,
                )

        # ---------------------------------------------------------
        # Sell Side Inducement
        # ---------------------------------------------------------

        if len(lows) >= 2:

            previous = lows[-2]

            current = lows[-1]

            distance = (

                previous.price
                -
                current.price

            )

            if (

                distance > 0

                and

                distance <= MIN_INDUCEMENT_DISTANCE

            ):

                return Inducement(

                    inducement_type=InducementType.SELL_SIDE,

                    price=current.price,

                    confidence=75.0,
                )

        return Inducement(

            inducement_type=InducementType.NONE,

            price=0.0,

            confidence=0.0,
        )
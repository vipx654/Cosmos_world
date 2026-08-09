"""
===============================================================================
COSMOS Dealing Range Engine

Institutional dealing range calculation.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.smc.models import DealingRange


class DealingRangeEngine:
    """
    Calculates the current institutional dealing range.

    The dealing range is built from the latest confirmed
    swing high and swing low.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> DealingRange:

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

        if not highs or not lows:

            return DealingRange(

                high=0.0,

                low=0.0,

                equilibrium=0.0,
            )

        latest_high = highs[-1].price

        latest_low = lows[-1].price

        equilibrium = (

            latest_high
            +
            latest_low

        ) / 2

        return DealingRange(

            high=latest_high,

            low=latest_low,

            equilibrium=equilibrium,
        )
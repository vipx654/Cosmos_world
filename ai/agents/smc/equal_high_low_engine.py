"""
===============================================================================
COSMOS Equal High / Equal Low Engine

Institutional liquidity level detection.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.smc.constants import (
    EQUAL_LEVEL_TOLERANCE,
    MIN_EQUAL_TOUCHES,
)

from ai.agents.smc.models import EqualLevel


class EqualHighLowEngine:
    """
    Detects Equal Highs and Equal Lows.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> tuple[EqualLevel | None, EqualLevel | None]:

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

        equal_high = self._find_equal_levels(
            highs,
        )

        equal_low = self._find_equal_levels(
            lows,
        )

        return (
            equal_high,
            equal_low,
        )

    def _find_equal_levels(
        self,
        swings: list[SwingPoint],
    ) -> EqualLevel | None:

        if len(swings) < MIN_EQUAL_TOUCHES:

            return None

        latest = swings[-1]

        touches = 1

        for swing in reversed(swings[:-1]):

            distance = abs(
                latest.price
                -
                swing.price
            )

            if distance <= EQUAL_LEVEL_TOLERANCE:

                touches += 1

        if touches >= MIN_EQUAL_TOUCHES:

            return EqualLevel(

                price=latest.price,

                touches=touches,
            )

        return None
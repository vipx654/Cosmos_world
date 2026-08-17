"""
===============================================================================
COSMOS MSS Engine

Market Structure Shift Detection

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.market_structure.constants import (
    MIN_MSS_DISTANCE,
    MIN_EVENT_CONFIDENCE,
)

from ai.agents.market_structure.models import (
    MSSAnalysis,
    StructureDirection,
    StructureEvent,
    StructureEventType,
)


class MSSEngine:
    """
    Detects validated Market Structure Shifts.

    MSS represents a meaningful structural transition and is
    kept separate from CHOCH so downstream strategy agents
    can distinguish the two events.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> MSSAnalysis:

        # =========================================================================
        # SAFETY
        # =========================================================================

        if len(swings) < 6:
            return MSSAnalysis(
                detected=False,
                bullish=False,
                bearish=False,
                confidence=0.0,
            )

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

        if len(highs) < 2 or len(lows) < 2:
            return MSSAnalysis(
                detected=False,
                bullish=False,
                bearish=False,
                confidence=0.0,
            )

        # =========================================================================
        # BULLISH MSS
        #
        # Current high breaks the previous structural high.
        # =========================================================================

        previous_high = highs[-2]
        current_high = highs[-1]

        high_distance = abs(
            current_high.index - previous_high.index
        )

        if (
            current_high.price > previous_high.price
            and high_distance >= MIN_MSS_DISTANCE
        ):
            displacement = (
                current_high.price
                - previous_high.price
            )

            confidence = 85.0

            confirmed = (
                confidence >= MIN_EVENT_CONFIDENCE
            )

            event = StructureEvent(
                event_type=StructureEventType.MSS,
                direction=StructureDirection.BULLISH,
                broken_price=previous_high.price,
                swing_index=current_high.index,
                confidence=confidence,
                confirmed=confirmed,
                displacement=displacement,
                strength=min(
                    100.0,
                    confidence,
                ),
                reasons=[
                    "Bullish structural shift detected.",
                    "Current high exceeded previous structural high.",
                ],
            )

            return MSSAnalysis(
                detected=True,
                bullish=True,
                bearish=False,
                confidence=confidence,
                event=event,
                reasons=list(event.reasons),
            )

        # =========================================================================
        # BEARISH MSS
        #
        # Current low breaks the previous structural low.
        # =========================================================================

        previous_low = lows[-2]
        current_low = lows[-1]

        low_distance = abs(
            current_low.index - previous_low.index
        )

        if (
            current_low.price < previous_low.price
            and low_distance >= MIN_MSS_DISTANCE
        ):
            displacement = (
                previous_low.price
                - current_low.price
            )

            confidence = 85.0

            confirmed = (
                confidence >= MIN_EVENT_CONFIDENCE
            )

            event = StructureEvent(
                event_type=StructureEventType.MSS,
                direction=StructureDirection.BEARISH,
                broken_price=previous_low.price,
                swing_index=current_low.index,
                confidence=confidence,
                confirmed=confirmed,
                displacement=displacement,
                strength=min(
                    100.0,
                    confidence,
                ),
                reasons=[
                    "Bearish structural shift detected.",
                    "Current low fell below previous structural low.",
                ],
            )

            return MSSAnalysis(
                detected=True,
                bullish=False,
                bearish=True,
                confidence=confidence,
                event=event,
                reasons=list(event.reasons),
            )

        # =========================================================================
        # NO MSS
        # =========================================================================

        return MSSAnalysis(
            detected=False,
            bullish=False,
            bearish=False,
            confidence=0.0,
            event=None,
            reasons=[
                "No validated market structure shift detected.",
            ],
        )
"""
===============================================================================
COSMOS Structure Engine

Detects institutional market structure.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.market_structure.models import StructureBias


@dataclass(slots=True)
class StructureAnalysis:
    """
    Raw market structure before BOS / CHOCH.
    """

    higher_highs: int

    higher_lows: int

    lower_highs: int

    lower_lows: int

    bias: StructureBias


class StructureEngine:
    """
    Reads swing points and determines the
    current market structure.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> StructureAnalysis:

        hh = 0
        hl = 0
        lh = 0
        ll = 0

        previous_high = None
        previous_low = None

        for swing in swings:

            if swing.swing_type == SwingType.HIGH:

                if previous_high is not None:

                    if swing.price > previous_high:

                        hh += 1

                    else:

                        lh += 1

                previous_high = swing.price

            elif swing.swing_type == SwingType.LOW:

                if previous_low is not None:

                    if swing.price > previous_low:

                        hl += 1

                    else:

                        ll += 1

                previous_low = swing.price

        bias = StructureBias.NEUTRAL

        if hh > lh and hl > ll:

            bias = StructureBias.BULLISH

        elif lh > hh and ll > hl:

            bias = StructureBias.BEARISH

        return StructureAnalysis(

            higher_highs=hh,

            higher_lows=hl,

            lower_highs=lh,

            lower_lows=ll,

            bias=bias,
        )
"""
===============================================================================
COSMOS Dow Theory Engine

Converts swing points into market structure using
Higher High (HH), Higher Low (HL),
Lower High (LH), Lower Low (LL).

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.models import SwingType
from ai.models import SwingPoint

from ai.agents.trend.models import StructureType


class DowEngine:
    """
    Dow Theory structure engine.
    """

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> list[StructureType]:

        structures: list[StructureType] = []

        previous_high: SwingPoint | None = None
        previous_low: SwingPoint | None = None

        for swing in swings:

            # -------------------------------------------------------------
            # HIGH
            # -------------------------------------------------------------

            if swing.swing_type == SwingType.HIGH:

                if previous_high is None:
                    previous_high = swing
                    continue

                if swing.price > previous_high.price:
                    structures.append(
                        StructureType.HH
                    )
                else:
                    structures.append(
                        StructureType.LH
                    )

                previous_high = swing

            # -------------------------------------------------------------
            # LOW
            # -------------------------------------------------------------

            else:

                if previous_low is None:
                    previous_low = swing
                    continue

                if swing.price > previous_low.price:
                    structures.append(
                        StructureType.HL
                    )
                else:
                    structures.append(
                        StructureType.LL
                    )

                previous_low = swing

        return structures
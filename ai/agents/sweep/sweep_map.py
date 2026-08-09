"""
===============================================================================
COSMOS Sweep Map Engine

Builds the institutional sweep map.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.sweep.models import (
    SweepMap,
    SweepObject,
)


class SweepMapEngine:
    """
    Creates the final SweepMap object.

    V1
    ----
    Organizes detected sweeps.

    V2
    ----
    Heatmap
    Cluster Density
    Session Distribution
    Historical Statistics
    """

    def build(
        self,
        buy_side: list[SweepObject],
        sell_side: list[SweepObject],
        fake_sweeps: list[SweepObject],
        confirmed: list[SweepObject],
    ) -> SweepMap:

        all_sweeps = (

            buy_side

            +

            sell_side

        )

        return SweepMap(

            buy_side=buy_side,

            sell_side=sell_side,

            fake_sweeps=fake_sweeps,

            confirmed=confirmed,

            all_sweeps=all_sweeps,

        )
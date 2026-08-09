"""
===============================================================================
COSMOS Session Sweep Engine

Detects which trading session a sweep belongs to.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from datetime import datetime

from ai.agents.sweep.models import SweepObject


class SessionSweepEngine:
    """
    Tags sweeps with the trading session.

    V1
    ----
    • Asian
    • London
    • New York

    V2
    ----
    • Kill Zones
    • Session Weight
    • Session Probability
    • Historical Session Statistics
    """

    def analyze(
        self,
        sweeps: list[SweepObject],
        candles,
    ) -> list[SweepObject]:

        if not sweeps:
            return sweeps

        for sweep in sweeps:

            if sweep.candle_index >= len(candles):
                continue

            candle = candles[sweep.candle_index]

            timestamp = getattr(
                candle,
                "time",
                None,
            )

            if timestamp is None:
                continue

            if isinstance(timestamp, datetime):

                hour = timestamp.hour

            else:

                hour = datetime.fromtimestamp(
                    timestamp
                ).hour

            # -----------------------------------------
            # Asian Session
            # -----------------------------------------

            if 0 <= hour < 8:

                sweep.session = "ASIAN"

                sweep.evidence.append(
                    "Asian Session Sweep"
                )

            # -----------------------------------------
            # London Session
            # -----------------------------------------

            elif 8 <= hour < 13:

                sweep.session = "LONDON"

                sweep.evidence.append(
                    "London Session Sweep"
                )

            # -----------------------------------------
            # New York Session
            # -----------------------------------------

            elif 13 <= hour < 22:

                sweep.session = "NEW_YORK"

                sweep.evidence.append(
                    "New York Session Sweep"
                )

            else:

                sweep.session = "AFTER_HOURS"

                sweep.evidence.append(
                    "After Hours Sweep"
                )

        return sweeps
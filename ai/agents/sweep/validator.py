"""
===============================================================================
COSMOS Sweep Validator

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.context import MarketContext


class SweepValidator:
    """
    Validates required data before
    Sweep Agent execution.
    """

    @staticmethod
    def validate(
        context: MarketContext,
    ) -> None:

        if context is None:

            raise ValueError(
                "MarketContext cannot be None."
            )

        if not context.candles:

            raise ValueError(
                "Candles are required."
            )

        required_agents = [

            "trend",

            "market_structure",

            "smc",

            "liquidity",

        ]

        missing = [

            agent

            for agent in required_agents

            if agent not in context.memory

        ]

        if missing:

            raise RuntimeError(

                "Missing dependencies: "

                + ", ".join(missing)

            )
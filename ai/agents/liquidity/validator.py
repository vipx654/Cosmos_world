"""
===============================================================================
COSMOS Liquidity Validator

Author: COSMOS Development Team
===============================================================================
"""

from __future__ import annotations

from ai.context import MarketContext


class LiquidityValidator:

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

        if "trend" not in context.memory:

            raise RuntimeError(
                "Trend Agent must run first."
            )

        if "market_structure" not in context.memory:

            raise RuntimeError(
                "Market Structure Agent must run first."
            )

        if "smc" not in context.memory:

            raise RuntimeError(
                "SMC Agent must run first."
            )
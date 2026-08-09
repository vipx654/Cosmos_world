"""
===============================================================================
COSMOS Trend Validator
===============================================================================
"""

from ai.context import MarketContext


class TrendValidator:

    @staticmethod
    def validate(
        context: MarketContext,
    ) -> None:

        if len(context.candles) < 20:
            raise ValueError(
                "Trend Agent requires at least 20 candles."
            )
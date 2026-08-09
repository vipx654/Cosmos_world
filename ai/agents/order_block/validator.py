"""
===============================================================================
COSMOS Order Block Validator

Validates the market context and required upstream data before Order Block
analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.context import MarketContext

from ai.agents.order_block.constants import (
    MIN_CANDLES_REQUIRED,
)


class OrderBlockValidator:
    """
    Validates prerequisites for the Order Block Agent.
    """

    @staticmethod
    def validate(
        context: MarketContext,
    ) -> None:
        """
        Validate the supplied MarketContext.
        """

        if context is None:
            raise ValueError(
                "MarketContext cannot be None."
            )

        candles = getattr(
            context,
            "candles",
            None,
        )

        if candles is None:
            raise ValueError(
                "MarketContext.candles is required."
            )

        if len(candles) < MIN_CANDLES_REQUIRED:
            raise ValueError(
                "Insufficient candles for Order Block analysis. "
                f"Required: {MIN_CANDLES_REQUIRED}, "
                f"received: {len(candles)}."
            )

        memory = getattr(
            context,
            "memory",
            None,
        )

        if memory is None:
            raise ValueError(
                "MarketContext.memory is required."
            )

        # ---------------------------------------------------------------------
        # Upstream agents are useful for confirmation and context.
        #
        # V1 does not require every upstream result to exist because the
        # detection engine can work directly from candle data.
        # ---------------------------------------------------------------------

        if not isinstance(memory, dict):
            raise TypeError(
                "MarketContext.memory must be a dictionary."
            )
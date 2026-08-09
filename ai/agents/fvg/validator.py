"""
===============================================================================
COSMOS Fair Value Gap Validator

Validates the market context before FVG analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.context import MarketContext

from ai.agents.fvg.constants import (
    MIN_CANDLES_REQUIRED,
)


class FVGValidator:
    """
    Validates prerequisites required by the FVG Agent.
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
                "Insufficient candles for FVG analysis. "
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

        if not isinstance(memory, dict):
            raise TypeError(
                "MarketContext.memory must be a dictionary."
            )
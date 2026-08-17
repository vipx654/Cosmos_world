"""
===============================================================================
COSMOS Fair Value Gap Validator

Validates the market context before FVG analysis.

The validator enforces only the minimum data required for FVG detection.
Optional context such as memory is preserved when available and can be
consumed by future FVG confluence and learning systems.

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

    Required:
        - MarketContext
        - candles
        - minimum candle count

    Optional:
        - memory

    Memory is intentionally optional because FVG detection itself does not
    require historical agent memory. Future versions may use it for:

        - historical FVG performance
        - symbol-specific behavior
        - session statistics
        - learned probability
        - multi-timeframe confluence
        - repeated FVG detection
        - adaptive thresholds
    """

    @staticmethod
    def validate(
        context: MarketContext,
    ) -> None:
        """
        Validate the supplied MarketContext.

        Raises:
            ValueError:
                If the context or candles are missing, or if there are not
                enough candles for FVG analysis.

            TypeError:
                If candles is not a collection-like object with a valid
                length.
        """

        # ---------------------------------------------------------------------
        # Context
        # ---------------------------------------------------------------------

        if context is None:
            raise ValueError(
                "MarketContext cannot be None."
            )

        # ---------------------------------------------------------------------
        # Candles
        # ---------------------------------------------------------------------

        candles = getattr(
            context,
            "candles",
            None,
        )

        if candles is None:
            raise ValueError(
                "MarketContext.candles is required."
            )

        # Validate that candles exposes a usable length.
        try:
            candle_count = len(candles)
        except TypeError as exc:
            raise TypeError(
                "MarketContext.candles must be a sized collection."
            ) from exc

        if candle_count < MIN_CANDLES_REQUIRED:
            raise ValueError(
                "Insufficient candles for FVG analysis. "
                f"Required: {MIN_CANDLES_REQUIRED}, "
                f"received: {candle_count}."
            )

        # ---------------------------------------------------------------------
        # Optional memory
        #
        # Memory is deliberately NOT required for FVG analysis.
        #
        # Some lightweight contexts and test contexts contain only candles.
        # The FVG engine must remain capable of operating on those contexts.
        # ---------------------------------------------------------------------

        memory = getattr(
            context,
            "memory",
            None,
        )

        if memory is not None and not isinstance(
            memory,
            dict,
        ):
            raise TypeError(
                "MarketContext.memory must be a dictionary when provided."
            )

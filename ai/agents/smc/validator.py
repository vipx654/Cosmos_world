"""
===============================================================================
COSMOS Smart Money Concept Validator

Validates the minimum market context required by the SMC engine.

The validator performs input validation only.
It does not generate signals or modify market data.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from typing import Any


class SMCValidationError(ValueError):
    """Raised when the SMC input context is invalid."""


class SMCValidator:
    """
    Validate MarketContext before SMC analysis.

    Requirements:
        - context must exist
        - candles must exist
        - candles must contain valid OHLC values
        - trend memory must contain swing information
    """

    @staticmethod
    def validate(context: Any) -> bool:

        # ---------------------------------------------------------------------
        # Context
        # ---------------------------------------------------------------------

        if context is None:
            raise SMCValidationError(
                "SMC context is missing"
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
            raise SMCValidationError(
                "SMC requires candle data"
            )

        if not candles:
            raise SMCValidationError(
                "SMC requires at least one candle"
            )

        # ---------------------------------------------------------------------
        # OHLC validation
        # ---------------------------------------------------------------------

        for index, candle in enumerate(candles):

            for field in (
                "open",
                "high",
                "low",
                "close",
            ):

                value = getattr(
                    candle,
                    field,
                    None,
                )

                if value is None:

                    raise SMCValidationError(
                        f"Candle {index} is missing "
                        f"{field}"
                    )

                try:
                    value = float(value)
                except (
                    TypeError,
                    ValueError,
                ):

                    raise SMCValidationError(
                        f"Candle {index} has invalid "
                        f"{field}: {value!r}"
                    )

                if value <= 0:

                    raise SMCValidationError(
                        f"Candle {index} has non-positive "
                        f"{field}: {value}"
                    )

            high = float(
                candle.high
            )

            low = float(
                candle.low
            )

            if high < low:

                raise SMCValidationError(
                    f"Candle {index} has high < low"
                )

        # ---------------------------------------------------------------------
        # Memory
        # ---------------------------------------------------------------------

        memory = getattr(
            context,
            "memory",
            None,
        )

        if memory is None:

            raise SMCValidationError(
                "SMC requires context.memory"
            )

        if not isinstance(
            memory,
            dict,
        ):

            raise SMCValidationError(
                "context.memory must be a dictionary"
            )

        # ---------------------------------------------------------------------
        # Trend memory
        # ---------------------------------------------------------------------

        trend_memory = memory.get(
            "trend"
        )

        if trend_memory is None:

            raise SMCValidationError(
                "SMC requires trend memory"
            )

        if not isinstance(
            trend_memory,
            dict,
        ):

            raise SMCValidationError(
                "context.memory['trend'] must be a dictionary"
            )

        if "swings" not in trend_memory:

            raise SMCValidationError(
                "SMC requires trend swings"
            )

        swings = trend_memory[
            "swings"
        ]

        if swings is None:

            raise SMCValidationError(
                "SMC trend swings cannot be None"
            )

        return True
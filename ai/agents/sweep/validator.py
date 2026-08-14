"""
===============================================================================
COSMOS Sweep Validator

Production validation for Sweep Agent dependencies and market context.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Real

from ai.context import MarketContext


class SweepValidator:
    """Validate all prerequisites required by the Sweep Agent."""

    REQUIRED_MEMORY_KEYS = (
        "trend",
        "market_structure",
        "smc",
        "liquidity",
    )

    @classmethod
    def validate(cls, context: MarketContext) -> None:
        """Validate the complete Sweep execution context."""

        if context is None:
            raise ValueError(
                "MarketContext cannot be None."
            )

        candles = getattr(
            context,
            "candles",
            None,
        )

        if not candles:
            raise ValueError(
                "Candles are required."
            )

        cls._validate_candles(candles)
        cls._validate_dependencies(context)

    @staticmethod
    def _validate_candles(candles) -> None:
        """Validate the minimum OHLC structure required by Sweep."""

        if len(candles) < 3:
            raise ValueError(
                "At least 3 candles are required "
                "for sweep detection."
            )

        required_fields = (
            "open",
            "high",
            "low",
            "close",
        )

        for index, candle in enumerate(candles):
            for field_name in required_fields:
                if not hasattr(candle, field_name):
                    raise ValueError(
                        f"Candle {index} is missing "
                        f"required field '{field_name}'."
                    )

                value = getattr(
                    candle,
                    field_name,
                )

                if not isinstance(value, Real):
                    raise TypeError(
                        f"Candle {index} field "
                        f"'{field_name}' must be numeric."
                    )

            if candle.high < candle.low:
                raise ValueError(
                    f"Candle {index} has high below low."
                )

            if candle.high < candle.open:
                raise ValueError(
                    f"Candle {index} high is below open."
                )

            if candle.high < candle.close:
                raise ValueError(
                    f"Candle {index} high is below close."
                )

            if candle.low > candle.open:
                raise ValueError(
                    f"Candle {index} low is above open."
                )

            if candle.low > candle.close:
                raise ValueError(
                    f"Candle {index} low is above close."
                )

    @classmethod
    def _validate_dependencies(
        cls,
        context: MarketContext,
    ) -> None:
        """Validate required upstream agent memory."""

        memory = getattr(
            context,
            "memory",
            None,
        )

        if not isinstance(memory, Mapping):
            raise TypeError(
                "MarketContext.memory must be a mapping."
            )

        missing = [
            key
            for key in cls.REQUIRED_MEMORY_KEYS
            if key not in memory
        ]

        if missing:
            raise RuntimeError(
                "Missing dependencies: "
                + ", ".join(missing)
            )

        liquidity = memory.get("liquidity")

        if not isinstance(liquidity, Mapping):
            raise TypeError(
                "Liquidity Agent memory must be a mapping."
            )

        if (
            "buy_side" not in liquidity
            and "sell_side" not in liquidity
        ):
            raise ValueError(
                "Liquidity Agent memory must contain "
                "buy_side or sell_side levels."
            )
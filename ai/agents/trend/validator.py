"""
===============================================================================
COSMOS Trend Agent Validator

Validates market context before Trend analysis.

The validator protects downstream Trend engines from malformed, insufficient,
unordered, or numerically invalid market data.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from math import isfinite

from ai.context import MarketContext
from ai.agents.trend.constants import (
    MAX_INVALID_CANDLE_RATIO,
    MIN_CANDLES,
    MIN_SWING_CANDLES,
    PREFERRED_CANDLES,
)


class TrendValidator:
    """
    Pre-analysis validation layer for the Trend Agent.

    Validation is intentionally performed before any swing, EMA, momentum,
    or trendline calculation.
    """

    @staticmethod
    def validate(
        context: MarketContext,
    ) -> None:
        """
        Validate the complete market context.

        Raises:
            ValueError: When market data is invalid or insufficient.
        """

        TrendValidator._validate_context(context)
        TrendValidator._validate_candles(context)

    # =========================================================================
    # CONTEXT
    # =========================================================================

    @staticmethod
    def _validate_context(
        context: MarketContext,
    ) -> None:

        if context is None:

            raise ValueError(
                "Trend Agent requires a valid MarketContext."
            )

        if not context.symbol:

            raise ValueError(
                "Trend Agent requires a market symbol."
            )

        if not context.timeframe:

            raise ValueError(
                "Trend Agent requires a timeframe."
            )

        if not isinstance(
            context.candles,
            list,
        ):

            raise ValueError(
                "Trend Agent candles must be provided as a list."
            )

    # =========================================================================
    # CANDLES
    # =========================================================================

    @staticmethod
    def _validate_candles(
        context: MarketContext,
    ) -> None:

        candles = context.candles

        if len(candles) < MIN_CANDLES:

            raise ValueError(
                f"Trend Agent requires at least "
                f"{MIN_CANDLES} candles."
            )

        invalid_count = 0

        for index, candle in enumerate(candles):

            if not TrendValidator._is_valid_candle(
                candle
            ):

                invalid_count += 1

                continue

            TrendValidator._validate_ohlc_relationship(
                candle,
                index,
            )

        invalid_ratio = (
            invalid_count / len(candles)
        )

        if invalid_ratio > MAX_INVALID_CANDLE_RATIO:

            raise ValueError(
                "Trend Agent received too many invalid candles: "
                f"{invalid_count}/{len(candles)} "
                f"({invalid_ratio * 100:.2f}%)."
            )

        TrendValidator._validate_timestamp_order(
            candles
        )

    # =========================================================================
    # SINGLE CANDLE
    # =========================================================================

    @staticmethod
    def _is_valid_candle(
        candle,
    ) -> bool:

        required = (
            candle.timestamp,
            candle.open,
            candle.high,
            candle.low,
            candle.close,
            candle.volume,
        )

        for value in required[1:]:

            try:

                numeric = float(value)

            except (
                TypeError,
                ValueError,
            ):

                return False

            if not isfinite(numeric):

                return False

        return candle.timestamp is not None

    # =========================================================================
    # OHLC INTEGRITY
    # =========================================================================

    @staticmethod
    def _validate_ohlc_relationship(
        candle,
        index: int,
    ) -> None:

        open_price = float(candle.open)
        high_price = float(candle.high)
        low_price = float(candle.low)
        close_price = float(candle.close)

        if high_price < low_price:

            raise ValueError(
                f"Invalid candle at index {index}: "
                "high is below low."
            )

        if not (
            low_price
            <= open_price
            <= high_price
        ):

            raise ValueError(
                f"Invalid candle at index {index}: "
                "open is outside candle range."
            )

        if not (
            low_price
            <= close_price
            <= high_price
        ):

            raise ValueError(
                f"Invalid candle at index {index}: "
                "close is outside candle range."
            )

        if float(candle.volume) < 0:

            raise ValueError(
                f"Invalid candle at index {index}: "
                "volume cannot be negative."
            )

    # =========================================================================
    # TIMESTAMP ORDER
    # =========================================================================

    @staticmethod
    def _validate_timestamp_order(
        candles,
    ) -> None:

        previous_timestamp = None

        for index, candle in enumerate(candles):

            if candle.timestamp is None:

                continue

            if (
                previous_timestamp is not None
                and candle.timestamp
                <= previous_timestamp
            ):

                raise ValueError(
                    f"Trend Agent candles must be strictly chronological. "
                    f"Invalid timestamp ordering at index {index}."
                )

            previous_timestamp = candle.timestamp

    # =========================================================================
    # DATA QUALITY
    # =========================================================================

    @staticmethod
    def preferred_history_available(
        context: MarketContext,
    ) -> bool:
        """
        Return True when enough history exists for stronger Trend analysis.

        This does not reject the context because shorter valid histories can
        still be useful for basic trend analysis.
        """

        return len(
            context.candles
        ) >= PREFERRED_CANDLES

    @staticmethod
    def swing_history_available(
        context: MarketContext,
    ) -> bool:
        """
        Return True when enough candles exist for meaningful swing detection.
        """

        return len(
            context.candles
        ) >= MIN_SWING_CANDLES

    @staticmethod
    def data_quality(
        context: MarketContext,
    ) -> dict[str, float | bool]:
        """
        Return a lightweight market-data quality report.
        """

        candles = context.candles

        if not candles:

            return {
                "valid": False,
                "quality": 0.0,
                "invalid_ratio": 1.0,
                "preferred_history": False,
            }

        invalid_count = sum(
            not TrendValidator._is_valid_candle(
                candle
            )
            for candle in candles
        )

        invalid_ratio = (
            invalid_count
            / len(candles)
        )

        quality = (
            1.0
            - invalid_ratio
        ) * 100.0

        return {
            "valid": (
                invalid_ratio
                <= MAX_INVALID_CANDLE_RATIO
            ),
            "quality": round(
                quality,
                2,
            ),
            "invalid_ratio": round(
                invalid_ratio,
                4,
            ),
            "preferred_history": (
                len(candles)
                >= PREFERRED_CANDLES
            ),
        }
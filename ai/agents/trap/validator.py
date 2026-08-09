"""
===============================================================================
COSMOS Trap Agent Validator

Validates candle/price data before Trap Agent analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ai.agents.trap.constants import (
    DEFAULT_LOOKBACK,
    MIN_CANDLES_REQUIRED,
    MIN_CANDLE_RANGE,
)


# =============================================================================
# VALIDATION RESULT
# =============================================================================


@dataclass
class TrapValidationResult:
    """
    Result returned by the Trap Agent validator.
    """

    valid: bool = False

    candle_count: int = 0

    lookback: int = DEFAULT_LOOKBACK

    errors: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =============================================================================
# VALIDATOR
# =============================================================================


class TrapValidator:
    """
    Validates candle data required by the Trap Agent.

    Required candle fields:

        open
        high
        low
        close

    Volume is optional because the Trap Agent can operate on price structure
    alone, although volume provides useful confirmation when available.
    """

    REQUIRED_FIELDS = (
        "open",
        "high",
        "low",
        "close",
    )

    OPTIONAL_FIELDS = (
        "volume",
        "timestamp",
        "time",
    )

    def validate(
        self,
        candles,
        lookback: int = DEFAULT_LOOKBACK,
    ) -> TrapValidationResult:
        """
        Validate candle data.

        Returns a TrapValidationResult rather than raising for ordinary
        validation failures.
        """

        errors: list[str] = []

        warnings: list[str] = []

        # ---------------------------------------------------------------------
        # None / empty input
        # ---------------------------------------------------------------------

        if candles is None:

            return TrapValidationResult(
                valid=False,
                candle_count=0,
                lookback=lookback,
                errors=[
                    "Candle data is None"
                ],
            )

        try:

            candle_list = list(
                candles
            )

        except TypeError:

            return TrapValidationResult(
                valid=False,
                candle_count=0,
                lookback=lookback,
                errors=[
                    "Candle data is not iterable"
                ],
            )

        candle_count = len(
            candle_list
        )

        # ---------------------------------------------------------------------
        # Minimum candles
        # ---------------------------------------------------------------------

        if (
            candle_count
            <
            MIN_CANDLES_REQUIRED
        ):

            errors.append(
                "Insufficient candles for trap analysis"
            )

        # ---------------------------------------------------------------------
        # Lookback validation
        # ---------------------------------------------------------------------

        try:

            lookback_value = int(
                lookback
            )

        except (
            TypeError,
            ValueError,
        ):

            errors.append(
                "Lookback must be an integer"
            )

            lookback_value = (
                DEFAULT_LOOKBACK
            )

        if lookback_value < 1:

            errors.append(
                "Lookback must be greater than zero"
            )

            lookback_value = (
                DEFAULT_LOOKBACK
            )

        # ---------------------------------------------------------------------
        # Check each candle
        # ---------------------------------------------------------------------

        invalid_candles = 0

        zero_range_candles = 0

        missing_volume = 0

        for index, candle in enumerate(
            candle_list
        ):

            # ================================================================
            # Access helper
            # ================================================================

            def get_value(
                name: str,
            ):
                if isinstance(
                    candle,
                    dict,
                ):

                    return candle.get(
                        name
                    )

                return getattr(
                    candle,
                    name,
                    None,
                )

            # ================================================================
            # Required fields
            # ================================================================

            missing_fields = []

            for field_name in (
                self.REQUIRED_FIELDS
            ):

                value = get_value(
                    field_name
                )

                if value is None:

                    missing_fields.append(
                        field_name
                    )

            if missing_fields:

                invalid_candles += 1

                errors.append(
                    f"Candle {index} missing fields: "
                    f"{', '.join(missing_fields)}"
                )

                continue

            # ================================================================
            # Numeric conversion
            # ================================================================

            try:

                open_price = float(
                    get_value("open")
                )

                high_price = float(
                    get_value("high")
                )

                low_price = float(
                    get_value("low")
                )

                close_price = float(
                    get_value("close")
                )

            except (
                TypeError,
                ValueError,
            ):

                invalid_candles += 1

                errors.append(
                    f"Candle {index} contains "
                    "non-numeric OHLC values"
                )

                continue

            # ================================================================
            # NaN / infinity protection
            # ================================================================

            values = (
                open_price,
                high_price,
                low_price,
                close_price,
            )

            if not all(
                self._is_finite(
                    value
                )
                for value in values
            ):

                invalid_candles += 1

                errors.append(
                    f"Candle {index} contains "
                    "non-finite OHLC values"
                )

                continue

            # ================================================================
            # OHLC consistency
            # ================================================================

            if high_price < low_price:

                invalid_candles += 1

                errors.append(
                    f"Candle {index}: "
                    "high is below low"
                )

                continue

            if (
                open_price < low_price
                or
                open_price > high_price
            ):

                invalid_candles += 1

                errors.append(
                    f"Candle {index}: "
                    "open is outside high/low range"
                )

                continue

            if (
                close_price < low_price
                or
                close_price > high_price
            ):

                invalid_candles += 1

                errors.append(
                    f"Candle {index}: "
                    "close is outside high/low range"
                )

                continue

            # ================================================================
            # Zero-range candle
            # ================================================================

            candle_range = (
                high_price
                -
                low_price
            )

            if (
                candle_range
                <=
                MIN_CANDLE_RANGE
            ):

                zero_range_candles += 1

            # ================================================================
            # Volume
            # ================================================================

            volume = get_value(
                "volume"
            )

            if volume is None:

                missing_volume += 1

            else:

                try:

                    volume_value = float(
                        volume
                    )

                    if (
                        not self._is_finite(
                            volume_value
                        )
                    ):

                        warnings.append(
                            f"Candle {index}: "
                            "volume is non-finite"
                        )

                    elif volume_value < 0.0:

                        errors.append(
                            f"Candle {index}: "
                            "volume cannot be negative"
                        )

                except (
                    TypeError,
                    ValueError,
                ):

                    warnings.append(
                        f"Candle {index}: "
                        "volume is not numeric"
                    )

        # ---------------------------------------------------------------------
        # Warnings
        # ---------------------------------------------------------------------

        if missing_volume:

            warnings.append(
                f"{missing_volume} candle(s) have no volume data; "
                "volume confirmation will be limited"
            )

        if zero_range_candles:

            warnings.append(
                f"{zero_range_candles} candle(s) have zero price range"
            )

        # ---------------------------------------------------------------------
        # Invalid candle ratio
        # ---------------------------------------------------------------------

        if candle_count > 0:

            invalid_ratio = (
                invalid_candles
                /
                candle_count
            )

            if invalid_ratio > 0.20:

                errors.append(
                    "More than 20% of candles are invalid"
                )

        # ---------------------------------------------------------------------
        # Final status
        # ---------------------------------------------------------------------

        valid = (
            len(errors) == 0
            and
            candle_count
            >=
            MIN_CANDLES_REQUIRED
        )

        return TrapValidationResult(

            valid=valid,

            candle_count=candle_count,

            lookback=lookback_value,

            errors=errors,

            warnings=warnings,

            metadata={
                "invalid_candles": (
                    invalid_candles
                ),
                "zero_range_candles": (
                    zero_range_candles
                ),
                "missing_volume": (
                    missing_volume
                ),
            },
        )

    # =========================================================================
    # FINITE VALUE CHECK
    # =========================================================================

    @staticmethod
    def _is_finite(
        value: float,
    ) -> bool:

        try:

            return (
                value == value
                and
                abs(value) != float("inf")
            )

        except (
            TypeError,
            ValueError,
        ):

            return False


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

trap_validator = TrapValidator()
"""
===============================================================================
COSMOS Volume Agent Validator

Validates candle and volume data before Volume Agent analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.volume.constants import (
    DEFAULT_LOOKBACK,
    MIN_LOOKBACK,
)


class VolumeValidator:
    """
    Validates the market context and candle volume data required by the
    Volume Agent.
    """

    @staticmethod
    def validate(
        context,
        lookback: int = DEFAULT_LOOKBACK,
    ) -> None:
        """
        Validate Volume Agent input.

        Raises:
            ValueError:
                When required market data is missing or invalid.

            TypeError:
                When input types are invalid.
        """

        # =====================================================================
        # CONTEXT
        # =====================================================================

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
                "MarketContext.candles is required "
                "for Volume analysis."
            )

        if not isinstance(
            candles,
            (list, tuple),
        ):
            raise TypeError(
                "MarketContext.candles must be "
                "a list or tuple."
            )

        # =====================================================================
        # LOOKBACK
        # =====================================================================

        if not isinstance(
            lookback,
            int,
        ):
            raise TypeError(
                "Volume lookback must be an integer."
            )

        if lookback < MIN_LOOKBACK:
            raise ValueError(
                f"Volume lookback must be at least "
                f"{MIN_LOOKBACK} candles."
            )

        if len(candles) < lookback:
            raise ValueError(
                "Insufficient candles for Volume analysis. "
                f"Required: {lookback}, "
                f"received: {len(candles)}."
            )

        # =====================================================================
        # CANDLE DATA
        # =====================================================================

        for index, candle in enumerate(
            candles
        ):

            if candle is None:
                raise ValueError(
                    f"Candle at index {index} is None."
                )

            required_fields = (
                "open",
                "high",
                "low",
                "close",
                "volume",
            )

            for field_name in required_fields:

                if not hasattr(
                    candle,
                    field_name,
                ):

                    raise ValueError(
                        f"Candle at index {index} "
                        f"is missing required field: "
                        f"{field_name}"
                    )

            # -------------------------------------------------------------
            # Numeric validation
            # -------------------------------------------------------------

            try:

                open_price = float(
                    candle.open
                )

                high_price = float(
                    candle.high
                )

                low_price = float(
                    candle.low
                )

                close_price = float(
                    candle.close
                )

                volume = float(
                    candle.volume
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    f"Invalid numeric candle data "
                    f"at index {index}."
                ) from exc

            # -------------------------------------------------------------
            # Price sanity
            # -------------------------------------------------------------

            if high_price < low_price:

                raise ValueError(
                    f"Candle at index {index} "
                    "has high below low."
                )

            if high_price < max(
                open_price,
                close_price,
            ):

                raise ValueError(
                    f"Candle at index {index} "
                    "has high below open/close."
                )

            if low_price > min(
                open_price,
                close_price,
            ):

                raise ValueError(
                    f"Candle at index {index} "
                    "has low above open/close."
                )

            # -------------------------------------------------------------
            # Volume sanity
            # -------------------------------------------------------------

            if volume < 0:

                raise ValueError(
                    f"Candle at index {index} "
                    "contains negative volume."
                )

        # =====================================================================
        # MEMORY
        # =====================================================================

        memory = getattr(
            context,
            "memory",
            None,
        )

        if memory is None:

            raise ValueError(
                "MarketContext.memory is required."
            )

        if not isinstance(
            memory,
            dict,
        ):

            raise TypeError(
                "MarketContext.memory must be a dictionary."
            )

    # =========================================================================
    # VOLUME TYPE
    # =========================================================================

    @staticmethod
    def detect_volume_type(
        context,
    ) -> str:
        """
        Determine the declared volume source.

        Priority:

        1. Explicit context.volume_type
        2. Explicit context metadata
        3. Default to tick volume

        COSMOS defaults to tick volume because this is the typical volume
        available for retail FX/CFD feeds.
        """

        explicit_type = getattr(
            context,
            "volume_type",
            None,
        )

        if explicit_type:

            return str(
                explicit_type
            ).lower()

        metadata = getattr(
            context,
            "metadata",
            None,
        )

        if isinstance(
            metadata,
            dict,
        ):

            volume_type = metadata.get(
                "volume_type"
            )

            if volume_type:

                return str(
                    volume_type
                ).lower()

        return "tick"
"""
===============================================================================
COSMOS Liquidity Validator

Institutional Liquidity Agent input and dependency validator.

Author: COSMOS Development Team
License: MIT
Version: 2.0.0
===============================================================================
"""

from __future__ import annotations

from math import isfinite
from typing import Any

from ai.context import MarketContext
from ai.models import AgentResult
from ai.models import SwingPoint


# =============================================================================
# VALIDATOR
# =============================================================================


class LiquidityValidator:
    """
    Validates everything required by the Liquidity Agent.

    Validation layers:

        1. Context validation
        2. Market data validation
        3. Upstream dependency validation
        4. Shared-memory validation
        5. Swing validation
        6. Numeric data validation
        7. Chart integration readiness

    The validator intentionally raises explicit errors instead of silently
    allowing corrupted upstream data into the Liquidity pipeline.
    """

    AGENT_NAME = "liquidity"

    REQUIRED_MEMORY = (
        "trend",
        "market_structure",
        "smc",
    )

    REQUIRED_UPSTREAM_RESULTS = (
        "trend",
        "market_structure",
        "smc",
    )

    MIN_CANDLES = 1

    MIN_SWINGS = 2

    # =========================================================================
    # PUBLIC VALIDATION
    # =========================================================================

    @staticmethod
    def validate(
        context: MarketContext,
    ) -> None:
        """
        Validate the complete Liquidity Agent input contract.

        Raises
        ------
        ValueError
            When market context or market data is invalid.

        RuntimeError
            When required upstream agents have not executed or their
            shared memory/result contracts are incomplete.
        """

        # ---------------------------------------------------------------------
        # Context
        # ---------------------------------------------------------------------

        LiquidityValidator._validate_context(
            context
        )

        # ---------------------------------------------------------------------
        # Raw Market Data
        # ---------------------------------------------------------------------

        LiquidityValidator._validate_market_data(
            context
        )

        # ---------------------------------------------------------------------
        # Upstream Dependencies
        # ---------------------------------------------------------------------

        LiquidityValidator._validate_dependencies(
            context
        )

        # ---------------------------------------------------------------------
        # Shared Memory
        # ---------------------------------------------------------------------

        LiquidityValidator._validate_shared_memory(
            context
        )

        # ---------------------------------------------------------------------
        # Market Structure Swings
        # ---------------------------------------------------------------------

        swings = (
            context.memory[
                "market_structure"
            ].get("swings")
        )

        LiquidityValidator._validate_swings(
            swings
        )

        # ---------------------------------------------------------------------
        # Chart Context
        # ---------------------------------------------------------------------

        LiquidityValidator._validate_chart_context(
            context
        )

    # =========================================================================
    # CONTEXT
    # =========================================================================

    @staticmethod
    def _validate_context(
        context: MarketContext,
    ) -> None:
        """
        Validate the MarketContext object itself.
        """

        if context is None:

            raise ValueError(
                "MarketContext cannot be None."
            )

        if not isinstance(
            context,
            MarketContext,
        ):

            raise TypeError(
                "context must be a MarketContext instance."
            )

        if not context.symbol:

            raise ValueError(
                "MarketContext symbol is required."
            )

        if not context.timeframe:

            raise ValueError(
                "MarketContext timeframe is required."
            )

        if not isinstance(
            context.memory,
            dict,
        ):

            raise TypeError(
                "MarketContext memory must be a dictionary."
            )

        if not isinstance(
            context.results,
            dict,
        ):

            raise TypeError(
                "MarketContext results must be a dictionary."
            )

    # =========================================================================
    # MARKET DATA
    # =========================================================================

    @staticmethod
    def _validate_market_data(
        context: MarketContext,
    ) -> None:
        """
        Validate raw candle data.
        """

        if not context.candles:

            raise ValueError(
                "Candles are required."
            )

        if len(context.candles) < (
            LiquidityValidator.MIN_CANDLES
        ):

            raise ValueError(
                "Insufficient candle data."
            )

        for index, candle in enumerate(
            context.candles
        ):

            if candle is None:

                raise ValueError(
                    f"Candle at index {index} cannot be None."
                )

            prices = (
                candle.open,
                candle.high,
                candle.low,
                candle.close,
                candle.volume,
            )

            for value in prices:

                if not isinstance(
                    value,
                    (int, float),
                ):

                    raise TypeError(
                        "Candle OHLCV values must be numeric."
                    )

                if not isfinite(
                    float(value)
                ):

                    raise ValueError(
                        "Candle OHLCV values must be finite."
                    )

            if candle.high < candle.low:

                raise ValueError(
                    f"Invalid candle at index {index}: "
                    "high cannot be below low."
                )

            if candle.volume < 0:

                raise ValueError(
                    f"Invalid candle at index {index}: "
                    "volume cannot be negative."
                )

    # =========================================================================
    # DEPENDENCIES
    # =========================================================================

    @staticmethod
    def _validate_dependencies(
        context: MarketContext,
    ) -> None:
        """
        Validate required upstream agents.

        Required order:

            Trend
                ↓
            Market Structure
                ↓
            SMC
                ↓
            Liquidity
        """

        for agent_name in (
            LiquidityValidator.REQUIRED_MEMORY
        ):

            if agent_name not in context.memory:

                display_name = (
                    agent_name.replace(
                        "_",
                        " ",
                    ).title()
                )

                raise RuntimeError(
                    f"{display_name} Agent must run first."
                )

        # ---------------------------------------------------------------------
        # Upstream result registry
        # ---------------------------------------------------------------------

        for agent_name in (
            LiquidityValidator.REQUIRED_UPSTREAM_RESULTS
        ):

            result = context.results.get(
                agent_name
            )

            if result is None:

                raise RuntimeError(
                    f"{agent_name} Agent result is missing."
                )

            if not isinstance(
                result,
                AgentResult,
            ):

                raise TypeError(
                    f"{agent_name} Agent result must be an AgentResult."
                )

            if not result.success:

                raise RuntimeError(
                    f"{agent_name} Agent did not complete successfully."
                )

            if not (
                0.0
                <= float(result.confidence)
                <= 100.0
            ):

                raise ValueError(
                    f"{agent_name} Agent confidence must be "
                    "between 0 and 100."
                )

    # =========================================================================
    # SHARED MEMORY
    # =========================================================================

    @staticmethod
    def _validate_shared_memory(
        context: MarketContext,
    ) -> None:
        """
        Validate upstream shared-memory structures.
        """

        trend_memory = context.memory.get(
            "trend"
        )

        if not isinstance(
            trend_memory,
            dict,
        ):

            raise TypeError(
                "Trend shared memory must be a dictionary."
            )

        market_structure_memory = (
            context.memory.get(
                "market_structure"
            )
        )

        if not isinstance(
            market_structure_memory,
            dict,
        ):

            raise TypeError(
                "Market Structure shared memory "
                "must be a dictionary."
            )

        smc_memory = context.memory.get(
            "smc"
        )

        if not isinstance(
            smc_memory,
            dict,
        ):

            raise TypeError(
                "SMC shared memory must be a dictionary."
            )

        # ---------------------------------------------------------------------
        # Market structure is the authoritative swing source for Liquidity.
        # ---------------------------------------------------------------------

        if "swings" not in (
            market_structure_memory
        ):

            raise RuntimeError(
                "Market Structure shared memory "
                "does not contain swings."
            )

    # =========================================================================
    # SWINGS
    # =========================================================================

    @staticmethod
    def _validate_swings(
        swings: Any,
    ) -> None:
        """
        Validate the swing sequence supplied by Market Structure.
        """

        if swings is None:

            raise ValueError(
                "Market Structure swings cannot be None."
            )

        if not isinstance(
            swings,
            list,
        ):

            raise TypeError(
                "Market Structure swings must be a list."
            )

        if len(swings) < (
            LiquidityValidator.MIN_SWINGS
        ):

            raise ValueError(
                "At least two swing points are required "
                "for Liquidity analysis."
            )

        previous_index: int | None = None

        for position, swing in enumerate(
            swings
        ):

            if not isinstance(
                swing,
                SwingPoint,
            ):

                raise TypeError(
                    f"Swing at position {position} "
                    "must be a SwingPoint."
                )

            if not isinstance(
                swing.index,
                int,
            ):

                raise TypeError(
                    "Swing index must be an integer."
                )

            if swing.index < 0:

                raise ValueError(
                    "Swing index cannot be negative."
                )

            if not isfinite(
                float(swing.price)
            ):

                raise ValueError(
                    "Swing price must be finite."
                )

            # -----------------------------------------------------------------
            # Swing ordering
            # -----------------------------------------------------------------

            if previous_index is not None:

                if swing.index <= previous_index:

                    raise ValueError(
                        "Swing points must be ordered "
                        "chronologically."
                    )

            previous_index = swing.index

    # =========================================================================
    # CHART CONTEXT
    # =========================================================================

    @staticmethod
    def _validate_chart_context(
        context: MarketContext,
    ) -> None:
        """
        Validate chart annotation infrastructure.

        Liquidity is a first-class visual analysis source in COSMOS.
        """

        if not hasattr(
            context,
            "annotations",
        ):

            raise RuntimeError(
                "MarketContext chart annotation support "
                "is required by Liquidity Agent."
            )

        if context.annotations is None:

            raise RuntimeError(
                "MarketContext annotations cannot be None."
            )

        if not isinstance(
            context.annotations,
            list,
        ):

            raise TypeError(
                "MarketContext annotations must be a list."
            )

    # =========================================================================
    # OPTIONAL SAFE VALIDATION HELPERS
    # =========================================================================

    @staticmethod
    def validate_price(
        price: float,
        field_name: str = "price",
    ) -> None:
        """
        Validate an individual price value.
        """

        if not isinstance(
            price,
            (int, float),
        ):

            raise TypeError(
                f"{field_name} must be numeric."
            )

        if not isfinite(
            float(price)
        ):

            raise ValueError(
                f"{field_name} must be finite."
            )

    @staticmethod
    def validate_score(
        score: float,
        field_name: str = "score",
    ) -> None:
        """
        Validate a normalized COSMOS score.
        """

        if not isinstance(
            score,
            (int, float),
        ):

            raise TypeError(
                f"{field_name} must be numeric."
            )

        if not isfinite(
            float(score)
        ):

            raise ValueError(
                f"{field_name} must be finite."
            )

        if not (
            0.0
            <= float(score)
            <= 100.0
        ):

            raise ValueError(
                f"{field_name} must be between 0 and 100."
            )
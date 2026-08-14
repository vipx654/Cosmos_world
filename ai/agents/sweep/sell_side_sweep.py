"""
===============================================================================
COSMOS Sell Side Sweep Engine

Production detection engine for institutional Sell Side Liquidity Sweeps.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from collections.abc import Sequence
from numbers import Real

from ai.agents.sweep.models import (
    SweepDirection,
    SweepObject,
    SweepStatus,
    SweepType,
)


class SellSideSweepEngine:
    """
    Detect Sell Side Liquidity Sweeps.

    A V1 Sell Side Sweep requires:

        1. Price trades below a Sell Side liquidity level.
        2. Candle closes back above that level.
        3. The candle therefore demonstrates rejection of lower prices.

    Additional evidence improves the initial score:

        - Strong rejection
        - Bullish close
        - Range expansion

    Confirmation is deliberately handled by ConfirmationEngine rather than
    being decided here.
    """

    BASE_CONFIDENCE = 60.0
    BASE_STRENGTH = 50.0
    BASE_PROBABILITY = 55.0

    STRONG_REJECTION_CONFIDENCE_BONUS = 10.0
    STRONG_REJECTION_STRENGTH_BONUS = 10.0
    STRONG_REJECTION_PROBABILITY_BONUS = 8.0

    BULLISH_CLOSE_CONFIDENCE_BONUS = 8.0
    BULLISH_CLOSE_STRENGTH_BONUS = 8.0
    BULLISH_CLOSE_PROBABILITY_BONUS = 7.0

    RANGE_EXPANSION_CONFIDENCE_BONUS = 8.0
    RANGE_EXPANSION_STRENGTH_BONUS = 8.0
    RANGE_EXPANSION_PROBABILITY_BONUS = 6.0

    MIN_CANDLES = 3
    MIN_SCORE = 0.0
    MAX_SCORE = 100.0

    SOURCE = "SellSideSweepEngine"

    def analyze(
        self,
        candles: Sequence[object] | None,
        liquidity_levels: Sequence[object] | None,
    ) -> list[SweepObject]:
        """
        Detect Sell Side liquidity sweeps.

        Returns
        -------
        list[SweepObject]
            One detected sweep per qualifying liquidity level.

        Notes
        -----
        The returned sweeps start in PENDING state. Later pipeline stages
        determine whether the sweep becomes CONFIRMED or FAILED.
        """

        if not candles:
            return []

        if len(candles) < self.MIN_CANDLES:
            return []

        if not liquidity_levels:
            return []

        sweeps: list[SweepObject] = []

        for level in liquidity_levels:

            if not self._is_sell_side_level(level):
                continue

            price = self._safe_price(level)

            if price is None:
                continue

            sweep = self._find_sweep_for_level(
                candles=candles,
                level_price=price,
            )

            if sweep is None:
                continue

            sweeps.append(sweep)

        return sweeps

    # =========================================================================
    # DETECTION
    # =========================================================================

    def _find_sweep_for_level(
        self,
        candles: Sequence[object],
        level_price: float,
    ) -> SweepObject | None:
        """
        Find the first qualifying sweep for one liquidity level.
        """

        for candle_index in range(
            2,
            len(candles),
        ):
            candle = candles[candle_index]
            previous = candles[candle_index - 1]

            candle_data = self._ohlc(candle)
            previous_data = self._ohlc(previous)

            if candle_data is None:
                continue

            if previous_data is None:
                continue

            (
                open_price,
                high_price,
                low_price,
                close_price,
            ) = candle_data

            (
                _previous_open,
                previous_high,
                previous_low,
                previous_close,
            ) = previous_data

            # -------------------------------------------------------------
            # Sell Side liquidity must be traded below.
            # -------------------------------------------------------------

            if low_price >= level_price:
                continue

            # -------------------------------------------------------------
            # Price must reclaim the liquidity level.
            # -------------------------------------------------------------

            if close_price <= level_price:
                continue

            sweep = self._build_sweep(
                candle=candle,
                candle_index=candle_index,
                level_price=level_price,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                previous_high=previous_high,
                previous_low=previous_low,
                previous_close=previous_close,
            )

            return sweep

        return None

    # =========================================================================
    # SWEEP CONSTRUCTION
    # =========================================================================

    def _build_sweep(
        self,
        *,
        candle: object,
        candle_index: int,
        level_price: float,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        previous_high: float,
        previous_low: float,
        previous_close: float,
    ) -> SweepObject:
        """
        Build and score one Sell Side Sweep.
        """

        confidence = self.BASE_CONFIDENCE
        strength = self.BASE_STRENGTH
        probability = self.BASE_PROBABILITY

        evidence: list[str] = [
            "Sell Side Liquidity Swept",
            "Price Traded Below Liquidity",
            "Close Reclaimed Liquidity",
        ]

        candle_range = max(
            0.0,
            high_price - low_price,
        )

        body_size = abs(
            close_price - open_price
        )

        penetration = max(
            0.0,
            level_price - low_price,
        )

        rejection = max(
            0.0,
            close_price - low_price,
        )

        # -------------------------------------------------------------
        # Strong rejection
        # -------------------------------------------------------------

        if rejection > body_size:
            confidence += (
                self.STRONG_REJECTION_CONFIDENCE_BONUS
            )

            strength += (
                self.STRONG_REJECTION_STRENGTH_BONUS
            )

            probability += (
                self.STRONG_REJECTION_PROBABILITY_BONUS
            )

            evidence.append(
                "Strong Rejection"
            )

        # -------------------------------------------------------------
        # Bullish close
        # -------------------------------------------------------------

        if close_price > open_price:
            confidence += (
                self.BULLISH_CLOSE_CONFIDENCE_BONUS
            )

            strength += (
                self.BULLISH_CLOSE_STRENGTH_BONUS
            )

            probability += (
                self.BULLISH_CLOSE_PROBABILITY_BONUS
            )

            evidence.append(
                "Bullish Close"
            )

        # -------------------------------------------------------------
        # Range expansion against previous candle
        # -------------------------------------------------------------

        previous_range = max(
            0.0,
            previous_high - previous_low,
        )

        if candle_range > previous_range:
            confidence += (
                self.RANGE_EXPANSION_CONFIDENCE_BONUS
            )

            strength += (
                self.RANGE_EXPANSION_STRENGTH_BONUS
            )

            probability += (
                self.RANGE_EXPANSION_PROBABILITY_BONUS
            )

            evidence.append(
                "Range Expansion"
            )

        confidence = self._clamp(
            confidence
        )

        strength = self._clamp(
            strength
        )

        probability = self._clamp(
            probability
        )

        timestamp = getattr(
            candle,
            "timestamp",
            None,
        )

        sweep = SweepObject(
            sweep_type=SweepType.SELL_SIDE,
            status=SweepStatus.PENDING,
            direction=SweepDirection.BULLISH,
            price=level_price,
            candle_index=candle_index,
            confidence=round(
                confidence,
                2,
            ),
            probability=round(
                probability,
                2,
            ),
            strength=round(
                strength,
                2,
            ),
            fake=False,
            session="",
            source=self.SOURCE,
            penetration=penetration,
            rejection=rejection,
            candle_range=candle_range,
            body_size=body_size,
            timestamp=timestamp,
            evidence=evidence,
        )

        sweep.clamp_scores()
        sweep.update_quality()

        return sweep

    # =========================================================================
    # VALIDATION HELPERS
    # =========================================================================

    @staticmethod
    def _is_sell_side_level(
        level: object,
    ) -> bool:
        """
        Safely determine whether a liquidity object is Sell Side.
        """

        liquidity_type = getattr(
            level,
            "liquidity_type",
            None,
        )

        if liquidity_type is SweepType:
            return False

        value = getattr(
            liquidity_type,
            "value",
            liquidity_type,
        )

        return value == "SELL_SIDE"

    @staticmethod
    def _safe_price(
        level: object,
    ) -> float | None:
        """
        Safely extract a valid liquidity price.
        """

        value = getattr(
            level,
            "price",
            None,
        )

        if not isinstance(
            value,
            Real,
        ):
            return None

        price = float(value)

        if price != price:
            return None

        if price in (
            float("inf"),
            float("-inf"),
        ):
            return None

        if price <= 0.0:
            return None

        return price

    @staticmethod
    def _ohlc(
        candle: object,
    ) -> tuple[
        float,
        float,
        float,
        float,
    ] | None:
        """
        Extract and validate OHLC values from a candle.
        """

        values = (
            getattr(candle, "open", None),
            getattr(candle, "high", None),
            getattr(candle, "low", None),
            getattr(candle, "close", None),
        )

        if not all(
            isinstance(value, Real)
            for value in values
        ):
            return None

        open_price = float(values[0])
        high_price = float(values[1])
        low_price = float(values[2])
        close_price = float(values[3])

        numeric_values = (
            open_price,
            high_price,
            low_price,
            close_price,
        )

        if any(
            value != value
            for value in numeric_values
        ):
            return None

        if any(
            value in (
                float("inf"),
                float("-inf"),
            )
            for value in numeric_values
        ):
            return None

        if high_price < low_price:
            return None

        if high_price < max(
            open_price,
            close_price,
        ):
            return None

        if low_price > min(
            open_price,
            close_price,
        ):
            return None

        return (
            open_price,
            high_price,
            low_price,
            close_price,
        )

    @classmethod
    def _clamp(
        cls,
        value: float,
    ) -> float:
        """
        Clamp a score to the valid 0-100 range.
        """

        return max(
            cls.MIN_SCORE,
            min(
                cls.MAX_SCORE,
                float(value),
            ),
        )
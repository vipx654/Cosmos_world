"""
===============================================================================
COSMOS Buy Side Sweep Engine

Production detector for institutional Buy Side Liquidity Sweeps.

A Buy Side sweep occurs when price trades above a known buy-side liquidity
level and then closes back below that level, indicating rejection.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from math import isfinite
from numbers import Real

from ai.agents.sweep.models import (
    SweepDirection,
    SweepObject,
    SweepStatus,
    SweepType,
)


class BuySideSweepEngine:
    """
    Detects buy-side liquidity sweeps.

    Detection only.

    Confirmation is intentionally delegated to ConfirmationEngine.
    """

    SOURCE = "BuySideSweepEngine"

    MIN_CANDLES = 3

    BASE_CONFIDENCE = 60.0
    BASE_PROBABILITY = 55.0
    BASE_STRENGTH = 50.0

    REJECTION_BONUS = 10.0
    BEARISH_CLOSE_BONUS = 8.0
    RANGE_EXPANSION_BONUS = 8.0

    PROBABILITY_REJECTION_BONUS = 8.0
    PROBABILITY_BEARISH_BONUS = 7.0
    PROBABILITY_EXPANSION_BONUS = 6.0

    def analyze(
        self,
        candles,
        liquidity_levels,
    ) -> list[SweepObject]:
        """
        Detect buy-side liquidity sweeps.

        A sweep requires:

        1. A BUY_SIDE liquidity level.
        2. Candle trades above the level.
        3. Candle closes back below the level.
        4. Candle data is structurally valid.

        Returns:
            List of detected SweepObject instances.
        """

        if candles is None or liquidity_levels is None:
            return []

        if len(candles) < self.MIN_CANDLES:
            return []

        sweeps: list[SweepObject] = []

        for level in liquidity_levels:

            if not self._is_buy_side_level(level):
                continue

            price = self._extract_level_price(level)

            if price is None:
                continue

            for index in range(2, len(candles)):

                candle = candles[index]
                previous = candles[index - 1]

                if not self._valid_candle(candle):
                    continue

                if not self._valid_candle(previous):
                    continue

                # ---------------------------------------------------------
                # Sweep condition
                # ---------------------------------------------------------

                if candle.high <= price:
                    continue

                # ---------------------------------------------------------
                # Rejection condition
                # ---------------------------------------------------------

                if candle.close >= price:
                    continue

                penetration = candle.high - price
                rejection = candle.high - candle.close
                candle_range = candle.high - candle.low
                body_size = abs(candle.close - candle.open)

                if candle_range <= 0:
                    continue

                confidence = self.BASE_CONFIDENCE
                probability = self.BASE_PROBABILITY
                strength = self.BASE_STRENGTH

                evidence: list[str] = [
                    "Buy Side Liquidity Swept",
                    "Price Traded Above Liquidity",
                    "Close Returned Below Liquidity",
                ]

                # ---------------------------------------------------------
                # Rejection
                # ---------------------------------------------------------

                if rejection > body_size:
                    confidence += self.REJECTION_BONUS
                    strength += self.REJECTION_BONUS
                    probability += self.PROBABILITY_REJECTION_BONUS

                    evidence.append(
                        "Strong Rejection"
                    )

                # ---------------------------------------------------------
                # Bearish close
                # ---------------------------------------------------------

                if candle.close < candle.open:
                    confidence += self.BEARISH_CLOSE_BONUS
                    strength += self.BEARISH_CLOSE_BONUS
                    probability += self.PROBABILITY_BEARISH_BONUS

                    evidence.append(
                        "Bearish Close"
                    )

                # ---------------------------------------------------------
                # Range expansion
                # ---------------------------------------------------------

                previous_range = (
                    previous.high - previous.low
                )

                if (
                    previous_range > 0
                    and candle_range > previous_range
                ):
                    confidence += self.RANGE_EXPANSION_BONUS
                    strength += self.RANGE_EXPANSION_BONUS
                    probability += (
                        self.PROBABILITY_EXPANSION_BONUS
                    )

                    evidence.append(
                        "Range Expansion"
                    )

                # ---------------------------------------------------------
                # Build object
                # ---------------------------------------------------------

                sweep = SweepObject(
                    sweep_type=SweepType.BUY_SIDE,
                    status=SweepStatus.PENDING,
                    direction=SweepDirection.BEARISH,
                    price=price,
                    candle_index=index,
                    confidence=self._clamp(confidence),
                    probability=self._clamp(probability),
                    strength=self._clamp(strength),
                    fake=False,
                    session="",
                    source=self.SOURCE,
                    penetration=penetration,
                    rejection=rejection,
                    candle_range=candle_range,
                    body_size=body_size,
                    timestamp=getattr(
                        candle,
                        "timestamp",
                        getattr(candle, "time", None),
                    ),
                    evidence=evidence,
                )

                sweep.clamp_scores()
                sweep.update_quality()

                sweeps.append(sweep)

                # One sweep per liquidity level.
                break

        return sweeps

    # =========================================================================
    # LEVEL VALIDATION
    # =========================================================================

    @staticmethod
    def _is_buy_side_level(level) -> bool:
        """Safely determine whether a liquidity level is buy-side."""

        liquidity_type = getattr(
            level,
            "liquidity_type",
            None,
        )

        if liquidity_type is None:
            return False

        value = getattr(
            liquidity_type,
            "value",
            liquidity_type,
        )

        return str(value) == "BUY_SIDE"

    @staticmethod
    def _extract_level_price(level) -> float | None:
        """Safely extract and validate liquidity price."""

        price = getattr(
            level,
            "price",
            None,
        )

        if not isinstance(price, Real):
            return None

        price = float(price)

        if not isfinite(price):
            return None

        return price

    # =========================================================================
    # CANDLE VALIDATION
    # =========================================================================

    @staticmethod
    def _valid_candle(candle) -> bool:
        """Validate the OHLC values required by the detector."""

        required = (
            "open",
            "high",
            "low",
            "close",
        )

        for field_name in required:

            value = getattr(
                candle,
                field_name,
                None,
            )

            if not isinstance(value, Real):
                return False

            if not isfinite(float(value)):
                return False

        open_price = float(candle.open)
        high_price = float(candle.high)
        low_price = float(candle.low)
        close_price = float(candle.close)

        if high_price < low_price:
            return False

        if high_price < max(
            open_price,
            close_price,
        ):
            return False

        if low_price > min(
            open_price,
            close_price,
        ):
            return False

        return True

    # =========================================================================
    # SCORE HELPERS
    # =========================================================================

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a score to the valid 0-100 range."""

        return max(
            0.0,
            min(
                100.0,
                float(value),
            ),
        )
"""
===============================================================================
COSMOS Sell Side Sweep Engine

Detects institutional Sell Side Liquidity Sweeps.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.sweep.models import (
    SweepObject,
    SweepDirection,
    SweepStatus,
    SweepType,
)


class SellSideSweepEngine:
    """
    Detects Sell Side Liquidity Sweeps.

    Sell Side Sweep =
        Previous Low taken
        +
        Immediate rejection
    """

    def analyze(
        self,
        candles,
        liquidity_levels,
    ) -> list[SweepObject]:

        sweeps: list[SweepObject] = []

        if len(candles) < 3:
            return sweeps

        for level in liquidity_levels:

            if level.liquidity_type.value != "SELL_SIDE":
                continue

            for i in range(2, len(candles)):

                candle = candles[i]

                previous = candles[i - 1]

                # -------------------------------------------------
                # Price sweeps below liquidity
                # -------------------------------------------------

                if candle.low >= level.price:
                    continue

                # -------------------------------------------------
                # Close back above liquidity
                # -------------------------------------------------

                if candle.close <= level.price:
                    continue

                confidence = 60.0

                strength = 50.0

                probability = 55.0

                evidence = []

                evidence.append(
                    "Previous Low Swept"
                )

                # -------------------------------------------------
                # Strong rejection
                # -------------------------------------------------

                rejection = (

                    candle.close

                    -

                    candle.low

                )

                body = abs(

                    candle.close

                    -

                    candle.open

                )

                if rejection > body:

                    confidence += 10

                    strength += 10

                    probability += 8

                    evidence.append(
                        "Strong Rejection"
                    )

                # -------------------------------------------------
                # Bullish Candle
                # -------------------------------------------------

                if candle.close > candle.open:

                    confidence += 8

                    strength += 8

                    probability += 7

                    evidence.append(
                        "Bullish Close"
                    )

                # -------------------------------------------------
                # Expansion
                # -------------------------------------------------

                expansion = (

                    candle.high

                    -

                    candle.low

                )

                previous_range = (

                    previous.high

                    -

                    previous.low

                )

                if expansion > previous_range:

                    confidence += 8

                    strength += 8

                    probability += 6

                    evidence.append(
                        "Range Expansion"
                    )

                confidence = min(confidence, 100)

                strength = min(strength, 100)

                probability = min(probability, 100)

                sweeps.append(

                    SweepObject(

                        sweep_type=SweepType.SELL_SIDE,

                        status=SweepStatus.CONFIRMED,

                        direction=SweepDirection.BULLISH,

                        price=level.price,

                        candle_index=i,

                        confidence=confidence,

                        probability=probability,

                        strength=strength,

                        fake=False,

                        source="SellSideSweepEngine",

                        evidence=evidence,

                    )

                )

                break

        return sweeps
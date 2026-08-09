"""
===============================================================================
COSMOS Volume Accumulation Engine

Detects possible accumulation-like price/volume behavior.

This is a heuristic signal, not proof of institutional activity.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.volume.constants import (
    MIN_ACCUMULATION_SCORE,
    STRONG_ACCUMULATION_SCORE,
)

from ai.agents.volume.models import (
    AccumulationSignal,
    VolumeDirection,
    VolumeSpike,
    VolumeTrend,
)

from ai.agents.volume.utils import (
    candle_body,
    candle_direction,
    candle_range,
    candle_volume,
    normalize_score,
    relative_volume,
)


class AccumulationEngine:
    """
    Detects possible accumulation conditions.

    Heuristic factors:

        - repeated activity near a relatively contained range
        - elevated volume
        - bullish price response
        - absorption-like candles
        - rising volume activity

    The engine deliberately avoids claiming knowledge of institutional intent.
    """

    def analyze(
        self,
        candles,
        spikes: list[VolumeSpike],
        trend: VolumeTrend | None,
    ) -> AccumulationSignal:

        if not candles:

            return AccumulationSignal(
                detected=False,
                score=0.0,
                confidence=0.0,
                evidence=[
                    "No candle data"
                ],
            )

        recent = list(
            candles[-10:]
        )

        if not recent:

            return AccumulationSignal(
                detected=False
            )

        score = 0.0

        evidence: list[str] = []

        # =====================================================================
        # 1. Range containment
        # =====================================================================

        highs = [
            float(
                getattr(
                    candle,
                    "high",
                    0.0,
                )
            )
            for candle in recent
        ]

        lows = [
            float(
                getattr(
                    candle,
                    "low",
                    0.0,
                )
            )
            for candle in recent
        ]

        highest = max(
            highs
        )

        lowest = min(
            lows
        )

        total_range = (
            highest - lowest
        )

        last_price = float(
            getattr(
                recent[-1],
                "close",
                0.0,
            )
        )

        # ---------------------------------------------------------------------
        # If price is contained in a relatively compact range, award one
        # accumulation point.
        # ---------------------------------------------------------------------

        candle_ranges = [
            candle_range(
                candle
            )
            for candle in recent
        ]

        average_range = (
            sum(candle_ranges)
            /
            len(candle_ranges)
            if candle_ranges
            else 0.0
        )

        if (
            average_range > 0.0
            and
            total_range
            <=
            average_range * 5.0
        ):

            score += 1.0

            evidence.append(
                "Price remains relatively contained"
            )

        # =====================================================================
        # 2. Elevated activity
        # =====================================================================

        volumes = [
            candle_volume(
                candle
            )
            for candle in recent
        ]

        average_volume = (
            sum(volumes)
            /
            len(volumes)
            if volumes
            else 0.0
        )

        current_volume = volumes[-1]

        rvol = relative_volume(
            current_volume,
            average_volume,
        )

        if rvol >= 1.50:

            score += 1.0

            evidence.append(
                f"Elevated activity at {rvol:.2f}x average"
            )

        # =====================================================================
        # 3. Bullish response
        # =====================================================================

        bullish_candles = 0

        bearish_candles = 0

        for candle in recent:

            direction = candle_direction(
                candle
            )

            if (
                direction
                == VolumeDirection.BULLISH
            ):

                bullish_candles += 1

            elif (
                direction
                == VolumeDirection.BEARISH
            ):

                bearish_candles += 1

        if bullish_candles > bearish_candles:

            score += 1.0

            evidence.append(
                "Bullish candles outnumber bearish candles"
            )

        # =====================================================================
        # 4. Bullish closing position
        # =====================================================================

        latest = recent[-1]

        latest_high = float(
            getattr(
                latest,
                "high",
                0.0,
            )
        )

        latest_low = float(
            getattr(
                latest,
                "low",
                0.0,
            )
        )

        latest_close = float(
            getattr(
                latest,
                "close",
                0.0,
            )
        )

        latest_range = (
            latest_high
            -
            latest_low
        )

        if latest_range > 0.0:

            close_position = (
                latest_close
                -
                latest_low
            ) / latest_range

            if close_position >= 0.65:

                score += 1.0

                evidence.append(
                    "Latest candle closes in upper range"
                )

        # =====================================================================
        # 5. Absorption-like behavior
        # =====================================================================

        absorption_count = 0

        for candle in recent:

            range_value = candle_range(
                candle
            )

            body_value = candle_body(
                candle
            )

            volume_value = candle_volume(
                candle
            )

            if range_value <= 0.0:

                continue

            body_ratio = (
                body_value
                /
                range_value
            )

            if (
                body_ratio <= 0.45
                and
                volume_value
                >=
                average_volume
                * 1.25
            ):

                absorption_count += 1

        if absorption_count >= 2:

            score += 1.0

            evidence.append(
                "Multiple high-activity candles "
                "show relatively contained bodies"
            )

        # =====================================================================
        # 6. Rising volume trend
        # =====================================================================

        if trend is not None:

            if trend.rising:

                score += 1.0

                evidence.append(
                    "Volume trend is rising"
                )

        # =====================================================================
        # 7. Recent bullish spike
        # =====================================================================

        bullish_spike = False

        for spike in spikes:

            if (
                spike.index
                <
                len(candles) - 5
            ):

                continue

            if (
                spike.direction
                == VolumeDirection.BULLISH
            ):

                bullish_spike = True

                break

        if bullish_spike:

            score += 1.0

            evidence.append(
                "Recent bullish volume spike detected"
            )

        # =====================================================================
        # FINAL SCORE
        # =====================================================================

        confidence = normalize_score(
            (
                score
                /
                STRONG_ACCUMULATION_SCORE
            )
            * 100.0
        )

        detected = (
            score
            >=
            MIN_ACCUMULATION_SCORE
        )

        if detected:

            evidence.append(
                "Possible accumulation-like behavior detected"
            )

        else:

            evidence.append(
                "Accumulation evidence insufficient"
            )

        # =====================================================================
        # Return
        # =====================================================================

        return AccumulationSignal(

            detected=detected,

            direction=(
                VolumeDirection.BULLISH
            ),

            score=round(
                score,
                2,
            ),

            confidence=round(
                confidence,
                2,
            ),

            evidence=evidence,
        )
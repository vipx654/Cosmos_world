"""
===============================================================================
COSMOS Volume Distribution Engine

Detects possible distribution-like price/volume behavior.

This is a heuristic signal, not proof of institutional selling.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.volume.constants import (
    MIN_DISTRIBUTION_SCORE,
    STRONG_DISTRIBUTION_SCORE,
)

from ai.agents.volume.models import (
    DistributionSignal,
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


class DistributionEngine:
    """
    Detects possible distribution-like conditions.

    Heuristic factors:

        - repeated activity inside a contained range
        - elevated volume
        - bearish price response
        - high-activity candles with relatively contained bodies
        - falling volume trend
        - recent bearish volume spikes

    The result is contextual evidence, not a claim about institutional intent.
    """

    def analyze(
        self,
        candles,
        spikes: list[VolumeSpike],
        trend: VolumeTrend | None,
    ) -> DistributionSignal:

        if not candles:

            return DistributionSignal(
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

            return DistributionSignal(
                detected=False
            )

        score = 0.0

        evidence: list[str] = []

        # =====================================================================
        # 1. RANGE CONTAINMENT
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
            highest
            -
            lowest
        )

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
        # 2. ELEVATED ACTIVITY
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
        # 3. BEARISH PRICE RESPONSE
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

        if bearish_candles > bullish_candles:

            score += 1.0

            evidence.append(
                "Bearish candles outnumber bullish candles"
            )

        # =====================================================================
        # 4. LOWER CLOSING POSITION
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

            if close_position <= 0.35:

                score += 1.0

                evidence.append(
                    "Latest candle closes in lower range"
                )

        # =====================================================================
        # 5. DISTRIBUTION / ABSORPTION-LIKE BEHAVIOR
        # =====================================================================

        distribution_count = 0

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
                average_volume * 1.25
            ):

                distribution_count += 1

        if distribution_count >= 2:

            score += 1.0

            evidence.append(
                "Multiple high-activity candles "
                "show relatively contained bodies"
            )

        # =====================================================================
        # 6. FALLING VOLUME TREND
        # =====================================================================

        if trend is not None:

            if trend.falling:

                score += 1.0

                evidence.append(
                    "Volume trend is falling"
                )

        # =====================================================================
        # 7. RECENT BEARISH SPIKE
        # =====================================================================

        bearish_spike = False

        recent_start = max(
            0,
            len(candles) - 5,
        )

        for spike in spikes:

            if spike.index < recent_start:
                continue

            if (
                spike.direction
                == VolumeDirection.BEARISH
            ):

                bearish_spike = True

                break

        if bearish_spike:

            score += 1.0

            evidence.append(
                "Recent bearish volume spike detected"
            )

        # =====================================================================
        # 8. FINAL SCORE
        # =====================================================================

        confidence = normalize_score(
            (
                score
                /
                STRONG_DISTRIBUTION_SCORE
            )
            * 100.0
        )

        detected = (
            score
            >=
            MIN_DISTRIBUTION_SCORE
        )

        if detected:

            evidence.append(
                "Possible distribution-like behavior detected"
            )

        else:

            evidence.append(
                "Distribution evidence insufficient"
            )

        # =====================================================================
        # RETURN
        # =====================================================================

        return DistributionSignal(

            detected=detected,

            direction=(
                VolumeDirection.BEARISH
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
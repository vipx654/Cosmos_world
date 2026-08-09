"""
===============================================================================
COSMOS Volume Trend Engine

Analyzes the direction and behavior of volume/activity over time.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.volume.constants import (
    DEFAULT_LOOKBACK,
    TREND_MIN_CHANGE,
    TREND_STRONG_CHANGE,
)

from ai.agents.volume.models import (
    VolumeDirection,
    VolumeState,
    VolumeTrend,
)

from ai.agents.volume.utils import (
    average_volume,
    candle_volume,
    classify_volume,
    normalize_score,
    relative_volume,
    simple_slope,
)


class VolumeTrendEngine:
    """
    Determines whether volume is:

        - rising
        - falling
        - stable

    The engine separates:

        volume direction
        from
        price direction

    This is intentional. Increasing volume by itself does not prove bullish
    or bearish pressure.
    """

    def analyze(
        self,
        candles,
        lookback: int = DEFAULT_LOOKBACK,
    ) -> VolumeTrend:

        if not candles:

            return VolumeTrend(
                direction=(
                    VolumeDirection.NEUTRAL
                ),
                state=(
                    VolumeState.NORMAL
                ),
                evidence=[
                    "No volume data"
                ],
            )

        # ---------------------------------------------------------------------
        # Use the most recent lookback candles.
        # ---------------------------------------------------------------------

        period = max(
            1,
            int(lookback),
        )

        recent = list(
            candles[-period:]
        )

        if not recent:

            return VolumeTrend()

        # ---------------------------------------------------------------------
        # Extract volume.
        # ---------------------------------------------------------------------

        volumes = [
            candle_volume(
                candle
            )
            for candle in recent
        ]

        current_volume = volumes[-1]

        average = average_volume(
            recent
        )

        relative = relative_volume(
            current_volume,
            average,
        )

        state = classify_volume(
            relative
        )

        # ---------------------------------------------------------------------
        # Volume slope.
        # ---------------------------------------------------------------------

        slope = simple_slope(
            volumes
        )

        # ---------------------------------------------------------------------
        # Normalize slope against average volume.
        #
        # This avoids interpreting a raw slope of 100 as equally important
        # across instruments with completely different volume scales.
        # ---------------------------------------------------------------------

        if average > 0.0:

            normalized_slope = (
                slope
                /
                average
            )

        else:

            normalized_slope = 0.0

        # ---------------------------------------------------------------------
        # Direction.
        # ---------------------------------------------------------------------

        if (
            normalized_slope
            >= TREND_MIN_CHANGE
        ):

            direction = (
                VolumeDirection.BULLISH
            )

            rising = True
            falling = False
            stable = False

        elif (
            normalized_slope
            <= -TREND_MIN_CHANGE
        ):

            direction = (
                VolumeDirection.BEARISH
            )

            rising = False
            falling = True
            stable = False

        else:

            direction = (
                VolumeDirection.NEUTRAL
            )

            rising = False
            falling = False
            stable = True

        # ---------------------------------------------------------------------
        # Trend strength.
        # ---------------------------------------------------------------------

        magnitude = abs(
            normalized_slope
        )

        if magnitude >= TREND_STRONG_CHANGE:

            confidence = 90.0

        elif magnitude >= TREND_MIN_CHANGE:

            confidence = 70.0

        else:

            confidence = 50.0

        # Strong current relative volume increases confidence in the activity
        # state, but does not change the direction by itself.

        if relative >= 2.0:

            confidence += 5.0

        elif relative >= 1.5:

            confidence += 3.0

        confidence = normalize_score(
            confidence
        )

        # ---------------------------------------------------------------------
        # Evidence.
        # ---------------------------------------------------------------------

        evidence: list[str] = []

        evidence.append(
            f"Current Volume: "
            f"{current_volume:.2f}"
        )

        evidence.append(
            f"Average Volume: "
            f"{average:.2f}"
        )

        evidence.append(
            f"Relative Volume: "
            f"{relative:.2f}x"
        )

        evidence.append(
            f"Volume Slope: "
            f"{slope:.6f}"
        )

        # ---------------------------------------------------------------------
        # State interpretation.
        # ---------------------------------------------------------------------

        if rising:

            evidence.append(
                "Volume Activity Rising"
            )

        elif falling:

            evidence.append(
                "Volume Activity Falling"
            )

        else:

            evidence.append(
                "Volume Activity Stable"
            )

        # ---------------------------------------------------------------------
        # Strong trend label.
        # ---------------------------------------------------------------------

        if magnitude >= TREND_STRONG_CHANGE:

            if rising:

                evidence.append(
                    "Strong Volume Expansion"
                )

            elif falling:

                evidence.append(
                    "Strong Volume Contraction"
                )

        # ---------------------------------------------------------------------
        # Build result.
        # ---------------------------------------------------------------------

        return VolumeTrend(

            direction=direction,

            state=state,

            slope=round(
                slope,
                8,
            ),

            current_volume=round(
                current_volume,
                8,
            ),

            average_volume=round(
                average,
                8,
            ),

            relative_volume=round(
                relative,
                4,
            ),

            rising=rising,

            falling=falling,

            stable=stable,

            confidence=round(
                confidence,
                2,
            ),

            evidence=evidence,
        )
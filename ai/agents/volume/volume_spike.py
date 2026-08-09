"""
===============================================================================
COSMOS Volume Spike Engine

Detects abnormal volume/activity spikes.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.volume.constants import (
    DEFAULT_LOOKBACK,
    MIN_SPIKE_RELATIVE_VOLUME,
    STRONG_SPIKE_RELATIVE_VOLUME,
    EXTREME_SPIKE_RELATIVE_VOLUME,
)

from ai.agents.volume.models import (
    VolumeDirection,
    VolumeSpike,
    VolumeState,
)

from ai.agents.volume.utils import (
    candle_direction,
    candle_volume,
    classify_volume,
    relative_volume,
    rolling_average_volume,
    volume_spike_strength,
)


class VolumeSpikeEngine:
    """
    Detects abnormal volume spikes.

    A spike is based on:

        current volume / rolling average volume

    The result is a VolumeSpike object for every detected spike.
    """

    def analyze(
        self,
        candles,
        lookback: int = DEFAULT_LOOKBACK,
    ) -> list[VolumeSpike]:

        if not candles:
            return []

        averages = rolling_average_volume(
            candles,
            lookback,
        )

        spikes: list[VolumeSpike] = []

        for index, candle in enumerate(
            candles
        ):

            volume = candle_volume(
                candle
            )

            average = averages[
                index
            ]

            relative = relative_volume(
                volume,
                average,
            )

            # -------------------------------------------------------------
            # Only classify as a spike when RVOL reaches the minimum
            # threshold.
            # -------------------------------------------------------------

            if relative < MIN_SPIKE_RELATIVE_VOLUME:
                continue

            state = classify_volume(
                relative
            )

            direction = candle_direction(
                candle
            )

            strength = volume_spike_strength(
                relative
            )

            evidence: list[str] = []

            # -------------------------------------------------------------
            # Evidence
            # -------------------------------------------------------------

            evidence.append(
                f"Relative Volume: {relative:.2f}x"
            )

            if relative >= EXTREME_SPIKE_RELATIVE_VOLUME:

                evidence.append(
                    "Extreme Volume Spike"
                )

            elif relative >= STRONG_SPIKE_RELATIVE_VOLUME:

                evidence.append(
                    "Strong Volume Spike"
                )

            else:

                evidence.append(
                    "Volume Spike"
                )

            # -------------------------------------------------------------
            # Direction
            # -------------------------------------------------------------

            if direction == VolumeDirection.BULLISH:

                evidence.append(
                    "Bullish Price Candle"
                )

            elif direction == VolumeDirection.BEARISH:

                evidence.append(
                    "Bearish Price Candle"
                )

            else:

                evidence.append(
                    "Neutral Price Candle"
                )

            # -------------------------------------------------------------
            # Confidence
            #
            # This is activity confidence, not probability of a profitable
            # trade.
            # -------------------------------------------------------------

            confidence = min(
                100.0,
                strength,
            )

            spike = VolumeSpike(

                index=index,

                volume=volume,

                average_volume=average,

                relative_volume=relative,

                state=state,

                direction=direction,

                strength=round(
                    strength,
                    2,
                ),

                confidence=round(
                    confidence,
                    2,
                ),

                evidence=evidence,
            )

            spikes.append(
                spike
            )

        return spikes
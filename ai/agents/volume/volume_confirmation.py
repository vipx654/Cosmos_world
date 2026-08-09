"""
===============================================================================
COSMOS Volume Confirmation Engine

Combines price action, volume spikes, and volume trend to determine whether
volume supports the current price movement.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.volume.constants import (
    MIN_CONFIRMATION_SCORE,
    STRONG_CONFIRMATION_SCORE,
)

from ai.agents.volume.models import (
    VolumeConfirmation,
    VolumeDirection,
    VolumeSpike,
    VolumeTrend,
)

from ai.agents.volume.utils import (
    candle_direction,
    candle_volume,
    normalize_score,
    relative_volume,
)


class VolumeConfirmationEngine:
    """
    Determines whether volume behavior supports price direction.

    Confirmation factors:

        1. Price direction
        2. Volume expansion
        3. Volume trend
        4. Volume spike
        5. Price/volume agreement

    The engine does NOT predict the next candle.
    """

    def analyze(
        self,
        candles,
        spikes: list[VolumeSpike],
        trend: VolumeTrend | None,
    ) -> VolumeConfirmation:

        if not candles:

            return VolumeConfirmation(
                confirmed=False,
                direction=(
                    VolumeDirection.NEUTRAL
                ),
                score=0.0,
                reasons=[
                    "No candle data"
                ],
            )

        # ---------------------------------------------------------------------
        # Current candle
        # ---------------------------------------------------------------------

        current = candles[-1]

        price_direction = candle_direction(
            current
        )

        current_volume = candle_volume(
            current
        )

        # ---------------------------------------------------------------------
        # Calculate recent average volume.
        # ---------------------------------------------------------------------

        volumes = [
            candle_volume(
                candle
            )
            for candle in candles
        ]

        average_volume = (
            sum(volumes)
            /
            len(volumes)
            if volumes
            else 0.0
        )

        rvol = relative_volume(
            current_volume,
            average_volume,
        )

        # ---------------------------------------------------------------------
        # Detect current spike.
        # ---------------------------------------------------------------------

        current_spike = None

        if spikes:

            current_index = len(
                candles
            ) - 1

            for spike in reversed(
                spikes
            ):

                if spike.index == current_index:

                    current_spike = spike

                    break

        spike_present = (
            current_spike is not None
        )

        # ---------------------------------------------------------------------
        # Initialize score.
        # ---------------------------------------------------------------------

        score = 0.0

        reasons: list[str] = []

        price_aligned = False

        volume_aligned = False

        trend_aligned = False

        divergence = False

        # ---------------------------------------------------------------------
        # 1. Price direction
        # ---------------------------------------------------------------------

        if (
            price_direction
            == VolumeDirection.BULLISH
        ):

            score += 1.0

            reasons.append(
                "Current price candle is bullish"
            )

        elif (
            price_direction
            == VolumeDirection.BEARISH
        ):

            score += 1.0

            reasons.append(
                "Current price candle is bearish"
            )

        else:

            reasons.append(
                "Current price candle is neutral"
            )

        # ---------------------------------------------------------------------
        # 2. Volume expansion
        # ---------------------------------------------------------------------

        if rvol >= 1.50:

            score += 1.0

            volume_aligned = True

            reasons.append(
                f"Volume expanded to {rvol:.2f}x average"
            )

        elif rvol >= 1.00:

            score += 0.5

            reasons.append(
                f"Volume is above/baseline at {rvol:.2f}x"
            )

        else:

            reasons.append(
                f"Volume is below average at {rvol:.2f}x"
            )

        # ---------------------------------------------------------------------
        # 3. Volume spike
        # ---------------------------------------------------------------------

        if spike_present:

            score += 1.0

            reasons.append(
                "Current candle has a volume spike"
            )

        # ---------------------------------------------------------------------
        # 4. Trend alignment
        # ---------------------------------------------------------------------

        if trend is not None:

            if (
                price_direction
                == VolumeDirection.BULLISH
                and
                trend.rising
            ):

                score += 1.0

                trend_aligned = True

                price_aligned = True

                reasons.append(
                    "Bullish price movement aligns "
                    "with rising volume"
                )

            elif (
                price_direction
                == VolumeDirection.BEARISH
                and
                trend.falling
            ):

                score += 1.0

                trend_aligned = True

                price_aligned = True

                reasons.append(
                    "Bearish price movement aligns "
                    "with falling volume"
                )

            # -------------------------------------------------------------
            # Divergence
            # -------------------------------------------------------------

            elif (
                price_direction
                == VolumeDirection.BULLISH
                and
                trend.falling
            ):

                divergence = True

                reasons.append(
                    "Bullish price movement with "
                    "falling volume"
                )

            elif (
                price_direction
                == VolumeDirection.BEARISH
                and
                trend.rising
            ):

                divergence = True

                reasons.append(
                    "Bearish price movement with "
                    "rising volume"
                )

        # ---------------------------------------------------------------------
        # 5. Direct price-volume agreement
        # ---------------------------------------------------------------------

        if (
            price_direction
            == VolumeDirection.BULLISH
            and
            rvol >= 1.50
        ):

            price_aligned = True

        elif (
            price_direction
            == VolumeDirection.BEARISH
            and
            rvol >= 1.50
        ):

            price_aligned = True

        # ---------------------------------------------------------------------
        # Divergence penalty
        # ---------------------------------------------------------------------

        if divergence:

            score -= 1.0

        # ---------------------------------------------------------------------
        # Normalize score.
        #
        # Maximum positive contribution:
        #
        #     price        = 1
        #     expansion    = 1
        #     spike        = 1
        #     trend        = 1
        #
        #     total        = 4
        # ---------------------------------------------------------------------

        normalized_score = normalize_score(
            (
                score
                /
                STRONG_CONFIRMATION_SCORE
            )
            * 100.0
        )

        # ---------------------------------------------------------------------
        # Confirmation decision
        # ---------------------------------------------------------------------

        confirmed = (
            score
            >=
            MIN_CONFIRMATION_SCORE
            and
            not divergence
        )

        # ---------------------------------------------------------------------
        # Strength classification
        # ---------------------------------------------------------------------

        if (
            confirmed
            and
            score >= STRONG_CONFIRMATION_SCORE
        ):

            reasons.append(
                "Strong volume confirmation"
            )

        elif confirmed:

            reasons.append(
                "Volume confirmation present"
            )

        else:

            if divergence:

                reasons.append(
                    "Volume divergence prevents confirmation"
                )

            else:

                reasons.append(
                    "Insufficient volume confirmation"
                )

        # ---------------------------------------------------------------------
        # Direction
        # ---------------------------------------------------------------------

        if confirmed:

            direction = (
                price_direction
            )

        else:

            direction = (
                VolumeDirection.NEUTRAL
            )

        return VolumeConfirmation(

            confirmed=confirmed,

            direction=direction,

            score=round(
                normalized_score,
                2,
            ),

            price_aligned=price_aligned,

            volume_aligned=volume_aligned,

            spike_present=spike_present,

            trend_aligned=trend_aligned,

            divergence=divergence,

            reasons=reasons,
        )
"""
===============================================================================
COSMOS Trap Volume Engine

Analyzes volume/activity around breakout and potential trap conditions.

For spot FX / MT5:
    Volume should be treated as activity evidence (often tick volume),
    not as centralized exchange-traded volume.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.trap.constants import (
    EXTREME_TRAP_RVOL,
    MIN_TRAP_RVOL,
    STRONG_TRAP_RVOL,
)

from ai.agents.trap.models import (
    BreakoutEvent,
    ReclaimEvent,
    TrapDirection,
    TrapVolumeEvidence,
)

from ai.agents.trap.utils import (
    average_volume,
    candle_volume,
    recent_candles,
    relative_volume,
    normalize_score,
)


class TrapVolumeEngine:
    """
    Evaluates volume/activity around a potential false breakout.

    The engine does not declare a trap by itself.

    It provides evidence such as:

        - elevated activity
        - strong activity
        - extreme activity
        - activity contraction after breakout
    """

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        candles,
        breakout: BreakoutEvent,
        reclaim: ReclaimEvent | None = None,
        lookback: int = 20,
    ) -> TrapVolumeEvidence:
        """
        Analyze volume around a breakout.

        A potential trap can show:

            1. unusual activity around the breakout
            2. followed by weaker activity during failure/reclaim

        Volume is supporting evidence, not a standalone decision.
        """

        if (
            breakout is None
            or
            not breakout.detected
        ):

            return TrapVolumeEvidence()

        try:

            candle_list = list(
                candles
            )

        except TypeError:

            return TrapVolumeEvidence()

        if not candle_list:

            return TrapVolumeEvidence()

        breakout_index = (
            breakout.candle_index
        )

        if breakout_index < 0:

            breakout_index = (
                len(candle_list) - 1
            )

        if breakout_index >= len(
            candle_list
        ):

            return TrapVolumeEvidence()

        breakout_candle = (
            candle_list[
                breakout_index
            ]
        )

        breakout_volume = (
            candle_volume(
                breakout_candle
            )
        )

        # =====================================================================
        # Historical volume
        # =====================================================================

        history_end = (
            breakout_index
        )

        history_start = max(
            0,
            history_end
            -
            max(
                1,
                int(
                    lookback
                ),
            ),
        )

        historical = candle_list[
            history_start:
            history_end
        ]

        baseline = average_volume(
            historical
        )

        # =====================================================================
        # Missing / unusable volume
        # =====================================================================

        if (
            breakout_volume <= 0.0
            or
            baseline <= 0.0
        ):

            return TrapVolumeEvidence(
                available=False,
                direction=(
                    breakout.direction
                ),
                evidence=[
                    "Volume data unavailable or insufficient"
                ],
            )

        # =====================================================================
        # Relative volume
        # =====================================================================

        rvol = relative_volume(
            breakout_volume,
            baseline,
        )

        elevated = (
            rvol >= MIN_TRAP_RVOL
        )

        strong = (
            rvol >= STRONG_TRAP_RVOL
        )

        evidence: list[str] = []

        if elevated:

            evidence.append(
                "Breakout activity exceeded recent average"
            )

        else:

            evidence.append(
                "Breakout activity was not elevated"
            )

        if strong:

            evidence.append(
                "Strong activity expansion detected"
            )

        if (
            rvol >= EXTREME_TRAP_RVOL
        ):

            evidence.append(
                "Extreme activity spike detected"
            )

        # =====================================================================
        # Post-breakout activity
        # =====================================================================

        post_breakout = []

        if reclaim is not None and reclaim.detected:

            reclaim_index = (
                breakout_index
                +
                max(
                    1,
                    reclaim.bars_after_breakout,
                )
            )

            if (
                reclaim_index
                < len(candle_list)
            ):

                post_breakout = (
                    recent_candles(
                        candle_list[
                            breakout_index
                            +
                            1:
                            reclaim_index
                            +
                            1
                        ],
                        3,
                    )
                )

        else:

            post_breakout = (
                recent_candles(
                    candle_list[
                        breakout_index
                        +
                        1:
                    ],
                    3,
                )
            )

        post_average = average_volume(
            post_breakout
        )

        # =====================================================================
        # Activity contraction
        # =====================================================================

        if (
            post_average > 0.0
            and
            breakout_volume > 0.0
        ):

            post_ratio = (
                post_average
                /
                breakout_volume
            )

            if post_ratio < 0.70:

                evidence.append(
                    "Activity contracted after breakout"
                )

            elif post_ratio < 0.90:

                evidence.append(
                    "Activity weakened after breakout"
                )

            else:

                evidence.append(
                    "Activity remained relatively active after breakout"
                )

        # =====================================================================
        # Score
        # =====================================================================

        strength = self._strength(
            rvol=rvol,
            post_average=post_average,
            breakout_volume=breakout_volume,
        )

        return TrapVolumeEvidence(

            available=True,

            relative_volume=round(
                rvol,
                3,
            ),

            elevated=elevated,

            strong=strong,

            direction=(
                breakout.direction
            ),

            strength=round(
                strength,
                2,
            ),

            evidence=evidence,
        )

    # =========================================================================
    # SINGLE CANDLE
    # =========================================================================

    def analyze_candle(
        self,
        candle,
        historical_candles,
        direction: TrapDirection = (
            TrapDirection.NEUTRAL
        ),
    ) -> TrapVolumeEvidence:
        """
        Analyze one candle against historical activity.
        """

        current_volume = candle_volume(
            candle
        )

        baseline = average_volume(
            historical_candles
        )

        if (
            current_volume <= 0.0
            or
            baseline <= 0.0
        ):

            return TrapVolumeEvidence(
                available=False,
                direction=direction,
                evidence=[
                    "Volume data unavailable"
                ],
            )

        rvol = relative_volume(
            current_volume,
            baseline,
        )

        evidence: list[str] = []

        if rvol >= EXTREME_TRAP_RVOL:

            evidence.append(
                "Extreme relative activity"
            )

        elif rvol >= STRONG_TRAP_RVOL:

            evidence.append(
                "Strong relative activity"
            )

        elif rvol >= MIN_TRAP_RVOL:

            evidence.append(
                "Elevated relative activity"
            )

        else:

            evidence.append(
                "Normal or weak relative activity"
            )

        return TrapVolumeEvidence(

            available=True,

            relative_volume=round(
                rvol,
                3,
            ),

            elevated=(
                rvol >= MIN_TRAP_RVOL
            ),

            strong=(
                rvol >= STRONG_TRAP_RVOL
            ),

            direction=direction,

            strength=round(
                normalize_score(
                    rvol
                    /
                    EXTREME_TRAP_RVOL
                    *
                    100.0
                ),
                2,
            ),

            evidence=evidence,
        )

    # =========================================================================
    # STRENGTH
    # =========================================================================

    @staticmethod
    def _strength(
        rvol: float,
        post_average: float,
        breakout_volume: float,
    ) -> float:
        """
        Convert activity characteristics into a 0-100 evidence score.

        Higher breakout activity increases the score.

        A large immediate contraction after the breakout also increases
        suspicion that the initial move lacked sustained participation.
        """

        if breakout_volume <= 0.0:

            return 0.0

        # -------------------------------------------------------------
        # Breakout activity component
        # -------------------------------------------------------------

        breakout_score = normalize_score(
            (
                rvol
                /
                EXTREME_TRAP_RVOL
            )
            *
            100.0
        )

        # -------------------------------------------------------------
        # Post-breakout contraction
        # -------------------------------------------------------------

        if post_average <= 0.0:

            contraction_score = 0.0

        else:

            post_ratio = (
                post_average
                /
                breakout_volume
            )

            contraction_score = (
                1.0
                -
                min(
                    1.0,
                    post_ratio,
                )
            ) * 100.0

        # Activity spike + subsequent contraction can be useful context for
        # a failed breakout, but it must not dominate the entire trap model.

        strength = (
            breakout_score * 0.45
            +
            contraction_score * 0.55
        )

        return normalize_score(
            strength
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

trap_volume_engine = TrapVolumeEngine()
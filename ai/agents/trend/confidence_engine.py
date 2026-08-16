"""
===============================================================================
COSMOS Trend Confidence Intelligence Engine
===============================================================================

Production-grade confidence fusion for the Trend Agent.

Combines:

    - EMA regime
    - EMA alignment
    - Momentum
    - Momentum persistence
    - Momentum exhaustion
    - Trendline quality
    - Trendline consistency
    - Cross-engine agreement

Design principles
-----------------
- Deterministic
- Bounded 0-100
- Contradiction-aware
- No standalone trading signal
- Downstream compatible
- Extensible for multi-timeframe fusion

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.agents.trend.ema_engine import (
    EMAAnalysis,
    EMA_REGIME_BULLISH,
    EMA_REGIME_BEARISH,
)

from ai.agents.trend.momentum_engine import (
    MomentumAnalysis,
)

from ai.agents.trend.trendline_engine import (
    TrendlineAnalysis,
)


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class ConfidenceBreakdown:
    """
    Detailed confidence decomposition.

    This is useful for:
        - debugging
        - dashboard explanation
        - agent audit
        - chart intelligence
        - future risk engine integration
    """

    ema_score: float = 0.0

    momentum_score: float = 0.0

    trendline_score: float = 0.0

    agreement_score: float = 0.0

    contradiction_penalty: float = 0.0

    exhaustion_penalty: float = 0.0

    total_score: float = 0.0


# =============================================================================
# ENGINE
# =============================================================================


class ConfidenceEngine:
    """
    Institutional Trend confidence fusion engine.

    IMPORTANT
    ---------
    Confidence represents analytical agreement.

    It is NOT:
        - probability of profit
        - probability of winning a trade
        - trade authorization
        - position sizing instruction
    """

    # =========================================================================
    # BASE WEIGHTS
    # =========================================================================

    EMA_WEIGHT = 0.40

    MOMENTUM_WEIGHT = 0.35

    TRENDLINE_WEIGHT = 0.25

    # =========================================================================
    # AGREEMENT
    # =========================================================================

    AGREEMENT_BONUS = 10.0

    TWO_ENGINE_AGREEMENT = 5.0

    # =========================================================================
    # PENALTIES
    # =========================================================================

    CONTRADICTION_PENALTY = 12.0

    EXHAUSTION_PENALTY = 8.0

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def _direction_from_ema(
        ema: EMAAnalysis,
    ) -> int:
        """
        Return:

            +1 bullish
             0 neutral
            -1 bearish
        """

        if ema.regime == EMA_REGIME_BULLISH:
            return 1

        if ema.regime == EMA_REGIME_BEARISH:
            return -1

        if ema.bullish_alignment:
            return 1

        if ema.bearish_alignment:
            return -1

        return 0

    # =========================================================================

    @staticmethod
    def _direction_from_momentum(
        momentum: MomentumAnalysis,
    ) -> int:
        """
        Return momentum direction.
        """

        if momentum.bullish:
            return 1

        if momentum.bearish:
            return -1

        if momentum.directional_score > 0:
            return 1

        if momentum.directional_score < 0:
            return -1

        return 0

    # =========================================================================

    @staticmethod
    def _direction_from_trendline(
        trendline: TrendlineAnalysis,
    ) -> int:
        """
        Return trendline direction.
        """

        if (
            trendline.bullish_trendline
            and not trendline.bearish_trendline
        ):
            return 1

        if (
            trendline.bearish_trendline
            and not trendline.bullish_trendline
        ):
            return -1

        if trendline.bullish_quality > (
            trendline.bearish_quality
        ):
            return 1

        if trendline.bearish_quality > (
            trendline.bullish_quality
        ):
            return -1

        return 0

    # =========================================================================
    # AGREEMENT
    # =========================================================================

    def _agreement_score(
        self,
        ema_direction: int,
        momentum_direction: int,
        trendline_direction: int,
    ) -> float:
        """
        Reward independent engines agreeing on direction.
        """

        directions = [
            ema_direction,
            momentum_direction,
            trendline_direction,
        ]

        active = [
            direction
            for direction in directions
            if direction != 0
        ]

        if len(active) < 2:
            return 0.0

        bullish_count = active.count(1)
        bearish_count = active.count(-1)

        if (
            bullish_count == len(active)
            or bearish_count == len(active)
        ):

            if len(active) == 3:
                return self.AGREEMENT_BONUS

            return self.TWO_ENGINE_AGREEMENT

        return 0.0

    # =========================================================================
    # CONTRADICTION
    # =========================================================================

    def _contradiction_penalty(
        self,
        ema_direction: int,
        momentum_direction: int,
        trendline_direction: int,
    ) -> float:
        """
        Penalize strong directional disagreement.
        """

        directions = [
            ema_direction,
            momentum_direction,
            trendline_direction,
        ]

        active = [
            direction
            for direction in directions
            if direction != 0
        ]

        if len(active) < 2:
            return 0.0

        bullish_count = active.count(1)
        bearish_count = active.count(-1)

        if bullish_count > 0 and bearish_count > 0:
            return self.CONTRADICTION_PENALTY

        return 0.0

    # =========================================================================
    # CALCULATE
    # =========================================================================

    def calculate(
        self,
        ema: EMAAnalysis,
        momentum: MomentumAnalysis,
        trendline: TrendlineAnalysis,
    ) -> float:
        """
        Calculate final Trend confidence.

        Returns
        -------
        float
            Bounded confidence score from 0 to 100.
        """

        # ---------------------------------------------------------------------
        # Base component scores
        # ---------------------------------------------------------------------

        ema_score = (
            ema.confidence
            * self.EMA_WEIGHT
        )

        momentum_score = (
            momentum.confidence
            * self.MOMENTUM_WEIGHT
        )

        trendline_score = (
            trendline.confidence
            * self.TRENDLINE_WEIGHT
        )

        # ---------------------------------------------------------------------
        # Directional agreement
        # ---------------------------------------------------------------------

        ema_direction = (
            self._direction_from_ema(
                ema
            )
        )

        momentum_direction = (
            self._direction_from_momentum(
                momentum
            )
        )

        trendline_direction = (
            self._direction_from_trendline(
                trendline
            )
        )

        agreement = self._agreement_score(
            ema_direction,
            momentum_direction,
            trendline_direction,
        )

        # ---------------------------------------------------------------------
        # Contradiction
        # ---------------------------------------------------------------------

        contradiction = (
            self._contradiction_penalty(
                ema_direction,
                momentum_direction,
                trendline_direction,
            )
        )

        # ---------------------------------------------------------------------
        # Momentum exhaustion
        # ---------------------------------------------------------------------

        exhaustion_penalty = 0.0

        if momentum.exhaustion:

            exhaustion_penalty = (
                self.EXHAUSTION_PENALTY
            )

        # ---------------------------------------------------------------------
        # Final score
        # ---------------------------------------------------------------------

        score = (
            ema_score
            + momentum_score
            + trendline_score
            + agreement
            - contradiction
            - exhaustion_penalty
        )

        score = max(
            0.0,
            min(
                score,
                100.0,
            ),
        )

        return round(
            score,
            2,
        )

    # =========================================================================
    # DETAILED ANALYSIS
    # =========================================================================

    def breakdown(
        self,
        ema: EMAAnalysis,
        momentum: MomentumAnalysis,
        trendline: TrendlineAnalysis,
    ) -> ConfidenceBreakdown:
        """
        Return complete confidence decomposition.

        This does not replace calculate().
        """

        ema_score = (
            ema.confidence
            * self.EMA_WEIGHT
        )

        momentum_score = (
            momentum.confidence
            * self.MOMENTUM_WEIGHT
        )

        trendline_score = (
            trendline.confidence
            * self.TRENDLINE_WEIGHT
        )

        ema_direction = (
            self._direction_from_ema(
                ema
            )
        )

        momentum_direction = (
            self._direction_from_momentum(
                momentum
            )
        )

        trendline_direction = (
            self._direction_from_trendline(
                trendline
            )
        )

        agreement = self._agreement_score(
            ema_direction,
            momentum_direction,
            trendline_direction,
        )

        contradiction = (
            self._contradiction_penalty(
                ema_direction,
                momentum_direction,
                trendline_direction,
            )
        )

        exhaustion_penalty = (
            self.EXHAUSTION_PENALTY
            if momentum.exhaustion
            else 0.0
        )

        total = (
            ema_score
            + momentum_score
            + trendline_score
            + agreement
            - contradiction
            - exhaustion_penalty
        )

        total = max(
            0.0,
            min(
                total,
                100.0,
            ),
        )

        return ConfidenceBreakdown(
            ema_score=round(
                ema_score,
                2,
            ),
            momentum_score=round(
                momentum_score,
                2,
            ),
            trendline_score=round(
                trendline_score,
                2,
            ),
            agreement_score=round(
                agreement,
                2,
            ),
            contradiction_penalty=round(
                contradiction,
                2,
            ),
            exhaustion_penalty=round(
                exhaustion_penalty,
                2,
            ),
            total_score=round(
                total,
                2,
            ),
        )
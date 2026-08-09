"""
===============================================================================
COSMOS Future Prediction Agent

Probabilistic forward-market assessment.

IMPORTANT:
    This agent does NOT claim to predict the exact future price.

It produces:

    - directional probability
    - expected return
    - expected range
    - volatility estimate
    - confidence
    - market regime
    - forecast horizon

The prediction is an additional decision signal for Strategy.
It does NOT bypass:
    Session
    Risk
    Execution

No future candle/data is allowed to enter the feature calculation.

Author: COSMOS Development Team
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from statistics import mean, pstdev
from typing import Any, Sequence


# =============================================================================
# ENUMS
# =============================================================================

class PredictionDirection(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class MarketRegime(str, Enum):
    TRENDING = "trending"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    UNKNOWN = "unknown"


# =============================================================================
# RESULT
# =============================================================================

@dataclass
class PredictionResult:

    direction: PredictionDirection = (
        PredictionDirection.NEUTRAL
    )

    probability_up: float = 0.50

    probability_down: float = 0.50

    probability_neutral: float = 0.0

    expected_return: float = 0.0

    expected_price: float | None = None

    lower_price: float | None = None

    upper_price: float | None = None

    volatility: float = 0.0

    confidence: float = 0.0

    regime: MarketRegime = (
        MarketRegime.UNKNOWN
    )

    horizon: int = 1

    valid: bool = False

    evidence: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =============================================================================
# CONFIG
# =============================================================================

@dataclass
class PredictionConfig:

    lookback: int = 50

    minimum_samples: int = 20

    horizon: int = 5

    trend_weight: float = 0.35

    momentum_weight: float = 0.25

    volatility_weight: float = 0.15

    structure_weight: float = 0.25

    neutral_band: float = 0.0005

    high_volatility_percentile: float = 0.80

    low_volatility_percentile: float = 0.20

    confidence_threshold: float = 55.0


# =============================================================================
# ENGINE
# =============================================================================

class FuturePredictionEngine:

    """
    Lightweight deterministic baseline predictor.

    This intentionally starts with transparent statistical features instead
    of an opaque ML model.

    Later, a trained model can implement the same prediction contract without
    changing Strategy/Risk/Execution interfaces.
    """

    def __init__(
        self,
        config: PredictionConfig | None = None,
    ) -> None:

        self.config = (
            config
            or
            PredictionConfig()
        )

    # =========================================================================
    # MAIN API
    # =========================================================================

    def predict(
        self,
        prices: Sequence[float],
        *,
        current_price: float | None = None,
        trend_signal: Any = None,
        structure_signal: Any = None,
        volume_signal: Any = None,
    ) -> PredictionResult:

        values = self._clean_prices(
            prices
        )

        if (
            len(values)
            <
            self.config.minimum_samples
        ):

            return PredictionResult(
                valid=False,
                evidence=[
                    "Insufficient historical samples"
                ],
                metadata={
                    "samples": len(values),
                    "required": (
                        self.config.minimum_samples
                    ),
                },
            )

        # =====================================================================
        # CURRENT PRICE
        # =====================================================================

        price = (
            float(current_price)
            if current_price is not None
            else
            values[-1]
        )

        if price <= 0.0:

            return PredictionResult(
                valid=False,
                evidence=[
                    "Current price must be positive"
                ],
            )

        # =====================================================================
        # RETURNS
        # =====================================================================

        returns = self._returns(
            values
        )

        if not returns:

            return PredictionResult(
                valid=False,
                evidence=[
                    "Unable to calculate returns"
                ],
            )

        # =====================================================================
        # FEATURES
        # =====================================================================

        trend = self._trend_score(
            values
        )

        momentum = self._momentum_score(
            values
        )

        volatility = self._volatility(
            returns
        )

        structure = (
            self._external_direction(
                structure_signal
            )
        )

        external_trend = (
            self._external_direction(
                trend_signal
            )
        )

        external_volume = (
            self._external_strength(
                volume_signal
            )
        )

        # =====================================================================
        # DIRECTION SCORE
        # =====================================================================

        statistical_score = (

            trend
            *
            self.config.trend_weight

            +

            momentum
            *
            self.config.momentum_weight

            +

            structure
            *
            self.config.structure_weight

            +

            external_volume
            *
            self.config.volatility_weight
        )

        # External trend agent provides additional context.
        statistical_score += (
            external_trend
            *
            0.10
        )

        # Clamp.
        statistical_score = max(
            -1.0,
            min(
                1.0,
                statistical_score,
            ),
        )

        # =====================================================================
        # PROBABILITIES
        # =====================================================================

        probability_up = (
            0.5
            +
            statistical_score
            *
            0.45
        )

        probability_up = max(
            0.01,
            min(
                0.99,
                probability_up,
            ),
        )

        probability_down = (
            1.0
            -
            probability_up
        )

        # =====================================================================
        # NEUTRAL BAND
        # =====================================================================

        neutral = (
            abs(
                statistical_score
            )
            <
            self.config.neutral_band
        )

        if neutral:

            direction = (
                PredictionDirection.NEUTRAL
            )

            probability_neutral = (
                0.20
            )

            probability_up = (
                probability_up
                *
                0.80
            )

            probability_down = (
                probability_down
                *
                0.80
            )

        elif statistical_score > 0:

            direction = (
                PredictionDirection.BULLISH
            )

            probability_neutral = 0.0

        else:

            direction = (
                PredictionDirection.BEARISH
            )

            probability_neutral = 0.0

        # =====================================================================
        # EXPECTED RETURN
        # =====================================================================

        expected_return = (
            statistical_score
            *
            volatility
            *
            sqrt(
                self.config.horizon
            )
        )

        # =====================================================================
        # EXPECTED PRICE
        # =====================================================================

        expected_price = (
            price
            *
            (
                1.0
                +
                expected_return
            )
        )

        # =====================================================================
        # EXPECTED RANGE
        # =====================================================================

        range_move = (
            price
            *
            volatility
            *
            sqrt(
                self.config.horizon
            )
        )

        lower_price = max(
            0.0,
            price
            -
            range_move,
        )

        upper_price = (
            price
            +
            range_move
        )

        # =====================================================================
        # REGIME
        # =====================================================================

        regime = self._regime(
            values,
            returns,
        )

        # =====================================================================
        # CONFIDENCE
        # =====================================================================

        confidence = (
            abs(
                statistical_score
            )
            *
            100.0
        )

        # More data improves confidence slightly.
        sample_factor = min(
            1.0,
            len(values)
            /
            (
                self.config.lookback
                *
                2.0
            ),
        )

        confidence *= (
            0.75
            +
            0.25
            *
            sample_factor
        )

        # High volatility reduces directional certainty.
        if (
            regime
            ==
            MarketRegime.HIGH_VOLATILITY
        ):

            confidence *= 0.85

        confidence = max(
            0.0,
            min(
                100.0,
                confidence,
            ),
        )

        # =====================================================================
        # EVIDENCE
        # =====================================================================

        evidence: list[str] = []

        if trend > 0.20:

            evidence.append(
                "Price trend is bullish"
            )

        elif trend < -0.20:

            evidence.append(
                "Price trend is bearish"
            )

        else:

            evidence.append(
                "Trend signal is weak"
            )

        if momentum > 0.20:

            evidence.append(
                "Momentum favors upside"
            )

        elif momentum < -0.20:

            evidence.append(
                "Momentum favors downside"
            )

        else:

            evidence.append(
                "Momentum is neutral"
            )

        if (
            regime
            ==
            MarketRegime.HIGH_VOLATILITY
        ):

            evidence.append(
                "High-volatility regime increases forecast uncertainty"
            )

        elif (
            regime
            ==
            MarketRegime.LOW_VOLATILITY
        ):

            evidence.append(
                "Low-volatility regime detected"
            )

        if confidence < (
            self.config.confidence_threshold
        ):

            evidence.append(
                "Forecast confidence is below confirmation threshold"
            )

        # =====================================================================
        # FINAL
        # =====================================================================

        return PredictionResult(

            direction=direction,

            probability_up=round(
                probability_up,
                4,
            ),

            probability_down=round(
                probability_down,
                4,
            ),

            probability_neutral=round(
                probability_neutral,
                4,
            ),

            expected_return=round(
                expected_return,
                6,
            ),

            expected_price=round(
                expected_price,
                8,
            ),

            lower_price=round(
                lower_price,
                8,
            ),

            upper_price=round(
                upper_price,
                8,
            ),

            volatility=round(
                volatility,
                6,
            ),

            confidence=round(
                confidence,
                2,
            ),

            regime=regime,

            horizon=self.config.horizon,

            valid=True,

            evidence=evidence,

            metadata={
                "samples": len(values),
                "trend_score": round(
                    trend,
                    4,
                ),
                "momentum_score": round(
                    momentum,
                    4,
                ),
                "structure_score": round(
                    structure,
                    4,
                ),
                "external_trend": round(
                    external_trend,
                    4,
                ),
                "external_volume": round(
                    external_volume,
                    4,
                ),
                "model": (
                    "deterministic_statistical_baseline"
                ),
                "future_data_used": False,
            },
        )

    # =========================================================================
    # PRICE CLEANING
    # =========================================================================

    @staticmethod
    def _clean_prices(
        prices: Sequence[float],
    ) -> list[float]:

        cleaned: list[float] = []

        for value in prices:

            try:

                number = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if number > 0.0:

                cleaned.append(
                    number
                )

        return cleaned

    # =========================================================================
    # RETURNS
    # =========================================================================

    @staticmethod
    def _returns(
        prices: Sequence[float],
    ) -> list[float]:

        result = []

        for previous, current in zip(
            prices[:-1],
            prices[1:],
        ):

            if previous <= 0:

                continue

            result.append(
                (
                    current
                    -
                    previous
                )
                /
                previous
            )

        return result

    # =========================================================================
    # TREND
    # =========================================================================

    def _trend_score(
        self,
        prices: Sequence[float],
    ) -> float:

        if len(prices) < 10:

            return 0.0

        short_window = min(
            10,
            len(prices),
        )

        long_window = min(
            30,
            len(prices),
        )

        short_mean = mean(
            prices[
                -short_window:
            ]
        )

        long_mean = mean(
            prices[
                -long_window:
            ]
        )

        if long_mean <= 0:

            return 0.0

        raw = (
            short_mean
            -
            long_mean
        ) / long_mean

        return max(
            -1.0,
            min(
                1.0,
                raw * 100.0,
            ),
        )

    # =========================================================================
    # MOMENTUM
    # =========================================================================

    def _momentum_score(
        self,
        prices: Sequence[float],
    ) -> float:

        if len(prices) < 6:

            return 0.0

        previous = prices[-6]

        current = prices[-1]

        if previous <= 0:

            return 0.0

        momentum = (
            current
            -
            previous
        ) / previous

        return max(
            -1.0,
            min(
                1.0,
                momentum * 100.0,
            ),
        )

    # =========================================================================
    # VOLATILITY
    # =========================================================================

    @staticmethod
    def _volatility(
        returns: Sequence[float],
    ) -> float:

        if len(returns) < 2:

            return 0.0

        return pstdev(
            returns
        )

    # =========================================================================
    # REGIME
    # =========================================================================

    def _regime(
        self,
        prices: Sequence[float],
        returns: Sequence[float],
    ) -> MarketRegime:

        if len(prices) < 20:

            return MarketRegime.UNKNOWN

        volatility = self._volatility(
            returns
        )

        trend = abs(
            self._trend_score(
                prices
            )
        )

        if volatility >= 0.01:

            return MarketRegime.HIGH_VOLATILITY

        if volatility <= 0.001:

            return MarketRegime.LOW_VOLATILITY

        if trend >= 45.0:

            return MarketRegime.TRENDING

        return MarketRegime.RANGING

    # =========================================================================
    # EXTERNAL DIRECTION
    # =========================================================================

    @staticmethod
    def _external_direction(
        result: Any,
    ) -> float:

        if result is None:

            return 0.0

        direction = getattr(
            result,
            "direction",
            getattr(
                result,
                "bias",
                None,
            ),
        )

        if direction is None:

            return 0.0

        value = str(
            getattr(
                direction,
                "value",
                direction,
            )
        ).lower()

        if value in (
            "bullish",
            "long",
            "buy",
            "up",
        ):

            return 1.0

        if value in (
            "bearish",
            "short",
            "sell",
            "down",
        ):

            return -1.0

        return 0.0

    # =========================================================================
    # EXTERNAL STRENGTH
    # =========================================================================

    @staticmethod
    def _external_strength(
        result: Any,
    ) -> float:

        if result is None:

            return 0.0

        for name in (
            "strength",
            "confidence",
            "score",
            "probability",
        ):

            value = getattr(
                result,
                name,
                None,
            )

            if value is None:

                continue

            try:

                number = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if number > 1.0:

                number /= 100.0

            direction = (
                FuturePredictionEngine
                ._external_direction(
                    result
                )
            )

            return max(
                -1.0,
                min(
                    1.0,
                    direction
                    *
                    number,
                ),
            )

        return 0.0


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

future_prediction_engine = (
    FuturePredictionEngine()
)


# =============================================================================
# PUBLIC API
# =============================================================================

def predict_future(
    prices: Sequence[float],
    **kwargs: Any,
) -> PredictionResult:

    return future_prediction_engine.predict(
        prices,
        **kwargs,
    )
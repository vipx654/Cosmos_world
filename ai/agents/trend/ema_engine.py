"""
===============================================================================
COSMOS EMA Intelligence Engine
===============================================================================

Production-grade Exponential Moving Average analysis.

Responsibilities:

    - EMA 20 / 50 / 100 / 200 calculation
    - Stable EMA seeding
    - Multi-EMA alignment
    - EMA spread analysis
    - Compression / expansion detection
    - Normalized EMA slope
    - Price-vs-EMA regime
    - Trend regime
    - Momentum confirmation
    - Confidence estimation
    - Chart annotation payload

Design principles:

    - Deterministic
    - Price-scale independent
    - No standalone trading signal
    - No API dependency
    - Downstream-agent compatible
    - Extensible for multi-timeframe analysis

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import MarketCandle


# =============================================================================
# ENUM-LIKE CONSTANTS
# =============================================================================

EMA_REGIME_BULLISH = "BULLISH"
EMA_REGIME_BEARISH = "BEARISH"
EMA_REGIME_MIXED = "MIXED"

PRICE_ABOVE = "ABOVE"
PRICE_BELOW = "BELOW"
PRICE_BETWEEN = "BETWEEN"

COMPRESSION = "COMPRESSION"
EXPANSION = "EXPANSION"
NORMAL = "NORMAL"


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class EMAAnalysis:
    """
    Complete EMA intelligence.

    Existing COSMOS fields are intentionally preserved so downstream
    components remain compatible.
    """

    # -------------------------------------------------------------------------
    # Core EMA values
    # -------------------------------------------------------------------------

    ema20: float
    ema50: float
    ema100: float
    ema200: float

    # -------------------------------------------------------------------------
    # Alignment
    # -------------------------------------------------------------------------

    bullish_alignment: bool
    bearish_alignment: bool

    # -------------------------------------------------------------------------
    # Volatility / spread state
    # -------------------------------------------------------------------------

    compression: bool
    expansion: bool

    # -------------------------------------------------------------------------
    # Legacy-compatible slope
    #
    # Kept as EMA20 - EMA50 for compatibility.
    # -------------------------------------------------------------------------

    slope: float

    # -------------------------------------------------------------------------
    # Confidence
    # -------------------------------------------------------------------------

    confidence: float

    # -------------------------------------------------------------------------
    # Extended intelligence
    # -------------------------------------------------------------------------

    ema20_slope: float = 0.0
    ema50_slope: float = 0.0
    ema100_slope: float = 0.0
    ema200_slope: float = 0.0

    normalized_slope: float = 0.0

    spread_20_50: float = 0.0
    spread_50_100: float = 0.0
    spread_100_200: float = 0.0

    price_regime: str = PRICE_BETWEEN

    regime: str = EMA_REGIME_MIXED

    volatility_state: str = NORMAL

    bullish_score: float = 0.0
    bearish_score: float = 0.0

    # -------------------------------------------------------------------------
    # Chart/UI metadata
    # -------------------------------------------------------------------------

    annotations: list[dict] | None = None


# =============================================================================
# ENGINE
# =============================================================================


class EMAEngine:
    """
    Production EMA intelligence engine.

    EMA is confirmation evidence.

    It must NEVER independently authorize a trade.
    """

    PERIODS = (
        20,
        50,
        100,
        200,
    )

    MIN_PERIOD = 20

    # Number of observations used to estimate EMA slope.
    SLOPE_LOOKBACK = 5

    # -------------------------------------------------------------------------
    # Spread thresholds
    #
    # These are percentages, not absolute price distances.
    # -------------------------------------------------------------------------

    COMPRESSION_THRESHOLD = 0.10
    EXPANSION_THRESHOLD = 0.50

    # -------------------------------------------------------------------------
    # Confidence components
    # -------------------------------------------------------------------------

    ALIGNMENT_WEIGHT = 35.0
    SLOPE_WEIGHT = 25.0
    PRICE_WEIGHT = 20.0
    SPREAD_WEIGHT = 20.0

    # =========================================================================
    # EMA CALCULATION
    # =========================================================================

    @staticmethod
    def calculate(
        prices: list[float],
        period: int,
    ) -> float:

        if not prices:
            raise ValueError(
                "EMA calculation requires price data."
            )

        if period <= 0:
            raise ValueError(
                "EMA period must be greater than zero."
            )

        # ---------------------------------------------------------------------
        # When insufficient data exists, use a simple mean of available data.
        #
        # This is deterministic and preferable to silently pretending that
        # the current close is a valid EMA.
        # ---------------------------------------------------------------------

        if len(prices) < period:
            return float(
                sum(prices) / len(prices)
            )

        multiplier = 2.0 / (
            period + 1.0
        )

        # Standard SMA seed.
        ema = sum(
            prices[:period]
        ) / period

        for price in prices[period:]:

            ema = (
                (price - ema)
                * multiplier
                + ema
            )

        return float(ema)

    # =========================================================================
    # EMA HISTORY
    # =========================================================================

    @classmethod
    def _history(
        cls,
        prices: list[float],
        period: int,
        points: int,
    ) -> list[float]:

        if not prices:
            return []

        if points <= 0:
            return []

        result: list[float] = []

        start = max(
            1,
            len(prices) - points,
        )

        for end in range(
            start,
            len(prices) + 1,
        ):

            result.append(
                cls.calculate(
                    prices[:end],
                    period,
                )
            )

        return result

    # =========================================================================
    # SLOPE
    # =========================================================================

    @staticmethod
    def _slope(
        values: list[float],
    ) -> float:

        if len(values) < 2:
            return 0.0

        return (
            values[-1]
            - values[-2]
        )

    # =========================================================================
    # NORMALIZED SLOPE
    # =========================================================================

    @staticmethod
    def _normalized_slope(
        slope: float,
        price: float,
    ) -> float:

        if price == 0:
            return 0.0

        return (
            slope / abs(price)
        ) * 100.0

    # =========================================================================
    # PERCENT SPREAD
    # =========================================================================

    @staticmethod
    def _spread(
        fast: float,
        slow: float,
    ) -> float:

        denominator = abs(slow)

        if denominator == 0:
            return 0.0

        return (
            (fast - slow)
            / denominator
        ) * 100.0

    # =========================================================================
    # PRICE REGIME
    # =========================================================================

    @staticmethod
    def _price_regime(
        price: float,
        ema20: float,
        ema50: float,
    ) -> str:

        if price > ema20 and price > ema50:
            return PRICE_ABOVE

        if price < ema20 and price < ema50:
            return PRICE_BELOW

        return PRICE_BETWEEN

    # =========================================================================
    # VOLATILITY / SPREAD STATE
    # =========================================================================

    @classmethod
    def _volatility_state(
        cls,
        spread: float,
    ) -> tuple[str, bool, bool]:

        absolute_spread = abs(
            spread
        )

        if (
            absolute_spread
            < cls.COMPRESSION_THRESHOLD
        ):

            return (
                COMPRESSION,
                True,
                False,
            )

        if (
            absolute_spread
            > cls.EXPANSION_THRESHOLD
        ):

            return (
                EXPANSION,
                False,
                True,
            )

        return (
            NORMAL,
            False,
            False,
        )

    # =========================================================================
    # CONFIDENCE
    # =========================================================================

    @classmethod
    def _confidence(
        cls,
        bullish: bool,
        bearish: bool,
        normalized_slope: float,
        price_regime: str,
        volatility_state: str,
    ) -> tuple[float, float, float]:

        bullish_score = 0.0
        bearish_score = 0.0

        # ---------------------------------------------------------------------
        # Alignment
        # ---------------------------------------------------------------------

        if bullish:
            bullish_score += (
                cls.ALIGNMENT_WEIGHT
            )

        elif bearish:
            bearish_score += (
                cls.ALIGNMENT_WEIGHT
            )

        # ---------------------------------------------------------------------
        # Slope
        # ---------------------------------------------------------------------

        slope_strength = min(
            abs(normalized_slope) * 100.0,
            cls.SLOPE_WEIGHT,
        )

        if normalized_slope > 0:
            bullish_score += slope_strength

        elif normalized_slope < 0:
            bearish_score += slope_strength

        # ---------------------------------------------------------------------
        # Price regime
        # ---------------------------------------------------------------------

        if price_regime == PRICE_ABOVE:
            bullish_score += cls.PRICE_WEIGHT

        elif price_regime == PRICE_BELOW:
            bearish_score += cls.PRICE_WEIGHT

        # ---------------------------------------------------------------------
        # Expansion confirms directional movement.
        # Compression reduces confidence.
        # ---------------------------------------------------------------------

        if volatility_state == EXPANSION:

            if bullish:
                bullish_score += cls.SPREAD_WEIGHT

            elif bearish:
                bearish_score += cls.SPREAD_WEIGHT

        elif volatility_state == COMPRESSION:

            bullish_score *= 0.85
            bearish_score *= 0.85

        total = (
            bullish_score
            + bearish_score
        )

        if total == 0:
            return (
                0.0,
                0.0,
                0.0,
            )

        confidence = max(
            bullish_score,
            bearish_score,
        )

        confidence = min(
            confidence,
            100.0,
        )

        return (
            round(confidence, 2),
            round(
                min(
                    bullish_score,
                    100.0,
                ),
                2,
            ),
            round(
                min(
                    bearish_score,
                    100.0,
                ),
                2,
            ),
        )

    # =========================================================================
    # ANALYSIS
    # =========================================================================

    def analyze(
        self,
        candles: list[MarketCandle],
    ) -> EMAAnalysis:

        if not candles:
            raise ValueError(
                "EMA analysis requires candles."
            )

        closes = [
            float(c.close)
            for c in candles
        ]

        if any(
            price <= 0
            for price in closes
        ):
            raise ValueError(
                "EMA analysis requires positive closing prices."
            )

        current_price = closes[-1]

        # ---------------------------------------------------------------------
        # Core EMAs
        # ---------------------------------------------------------------------

        ema20 = self.calculate(
            closes,
            20,
        )

        ema50 = self.calculate(
            closes,
            50,
        )

        ema100 = self.calculate(
            closes,
            100,
        )

        ema200 = self.calculate(
            closes,
            200,
        )

        # ---------------------------------------------------------------------
        # Alignment
        # ---------------------------------------------------------------------

        bullish = (
            ema20
            > ema50
            > ema100
            > ema200
        )

        bearish = (
            ema20
            < ema50
            < ema100
            < ema200
        )

        # ---------------------------------------------------------------------
        # EMA histories
        # ---------------------------------------------------------------------

        ema20_history = self._history(
            closes,
            20,
            self.SLOPE_LOOKBACK,
        )

        ema50_history = self._history(
            closes,
            50,
            self.SLOPE_LOOKBACK,
        )

        ema100_history = self._history(
            closes,
            100,
            self.SLOPE_LOOKBACK,
        )

        ema200_history = self._history(
            closes,
            200,
            self.SLOPE_LOOKBACK,
        )

        # ---------------------------------------------------------------------
        # Slopes
        # ---------------------------------------------------------------------

        ema20_slope = self._slope(
            ema20_history
        )

        ema50_slope = self._slope(
            ema50_history
        )

        ema100_slope = self._slope(
            ema100_history
        )

        ema200_slope = self._slope(
            ema200_history
        )

        normalized_slope = (
            self._normalized_slope(
                ema20_slope,
                current_price,
            )
        )

        # ---------------------------------------------------------------------
        # Spread
        # ---------------------------------------------------------------------

        spread_20_50 = self._spread(
            ema20,
            ema50,
        )

        spread_50_100 = self._spread(
            ema50,
            ema100,
        )

        spread_100_200 = self._spread(
            ema100,
            ema200,
        )

        # ---------------------------------------------------------------------
        # Compression / expansion
        # ---------------------------------------------------------------------

        volatility_state, compression, expansion = (
            self._volatility_state(
                spread_20_50
            )
        )

        # ---------------------------------------------------------------------
        # Price regime
        # ---------------------------------------------------------------------

        price_regime = self._price_regime(
            current_price,
            ema20,
            ema50,
        )

        # ---------------------------------------------------------------------
        # Overall EMA regime
        # ---------------------------------------------------------------------

        if bullish:
            regime = EMA_REGIME_BULLISH

        elif bearish:
            regime = EMA_REGIME_BEARISH

        else:
            regime = EMA_REGIME_MIXED

        # ---------------------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------------------

        (
            confidence,
            bullish_score,
            bearish_score,
        ) = self._confidence(
            bullish=bullish,
            bearish=bearish,
            normalized_slope=normalized_slope,
            price_regime=price_regime,
            volatility_state=volatility_state,
        )

        # ---------------------------------------------------------------------
        # Chart annotations
        # ---------------------------------------------------------------------

        annotations = [

            {
                "type": "EMA",
                "period": 20,
                "value": ema20,
                "locked": True,
                "source": "trend.ema",
            },

            {
                "type": "EMA",
                "period": 50,
                "value": ema50,
                "locked": True,
                "source": "trend.ema",
            },

            {
                "type": "EMA",
                "period": 100,
                "value": ema100,
                "locked": True,
                "source": "trend.ema",
            },

            {
                "type": "EMA",
                "period": 200,
                "value": ema200,
                "locked": True,
                "source": "trend.ema",
            },

            {
                "type": "EMA_REGIME",
                "regime": regime,
                "price_regime": price_regime,
                "volatility_state": volatility_state,
                "confidence": confidence,
                "locked": True,
                "source": "trend.ema",
            },
        ]

        return EMAAnalysis(

            # Existing fields
            ema20=ema20,
            ema50=ema50,
            ema100=ema100,
            ema200=ema200,

            bullish_alignment=bullish,
            bearish_alignment=bearish,

            compression=compression,
            expansion=expansion,

            # Compatibility field
            slope=ema20 - ema50,

            confidence=confidence,

            # Extended intelligence
            ema20_slope=ema20_slope,
            ema50_slope=ema50_slope,
            ema100_slope=ema100_slope,
            ema200_slope=ema200_slope,

            normalized_slope=normalized_slope,

            spread_20_50=spread_20_50,
            spread_50_100=spread_50_100,
            spread_100_200=spread_100_200,

            price_regime=price_regime,
            regime=regime,
            volatility_state=volatility_state,

            bullish_score=bullish_score,
            bearish_score=bearish_score,

            annotations=annotations,
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

ema_engine = EMAEngine()
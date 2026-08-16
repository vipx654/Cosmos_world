"""
===============================================================================
COSMOS Momentum Intelligence Engine
===============================================================================

Production-grade market momentum analysis.

Responsibilities
----------------
- Multi-horizon price velocity
- Normalized momentum
- Momentum acceleration
- Momentum persistence
- Volatility-normalized movement
- Bullish / bearish directional bias
- Momentum strength
- Exhaustion detection
- Confidence estimation
- Chart annotation payload

Design principles
-----------------
- Price-scale independent
- Deterministic
- No standalone trading signal
- No API dependency
- Downstream-agent compatible
- Suitable for FX, indices, metals and crypto

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import MarketCandle


# =============================================================================
# CONSTANTS
# =============================================================================

SHORT_LOOKBACK = 3
MEDIUM_LOOKBACK = 6
LONG_LOOKBACK = 12

VOLATILITY_LOOKBACK = 14

MINIMUM_CANDLES = 15

EPSILON = 1e-12


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class MomentumAnalysis:
    """
    Complete momentum intelligence.

    Existing COSMOS fields are preserved for compatibility.
    """

    # Legacy-compatible fields
    velocity: float
    acceleration: float

    bullish: bool
    bearish: bool

    confidence: float

    # Extended intelligence
    short_velocity: float = 0.0
    medium_velocity: float = 0.0
    long_velocity: float = 0.0

    normalized_velocity: float = 0.0
    normalized_acceleration: float = 0.0

    persistence: float = 0.0

    strength: float = 0.0

    exhaustion: bool = False

    volatility: float = 0.0

    directional_score: float = 0.0

    annotations: list[dict] | None = None


# =============================================================================
# ENGINE
# =============================================================================


class MomentumEngine:
    """
    Production-grade momentum intelligence engine.

    Momentum provides confirmation evidence.

    It must NEVER independently authorize a trade.
    """

    MINIMUM_CANDLES = MINIMUM_CANDLES

    SHORT_LOOKBACK = SHORT_LOOKBACK
    MEDIUM_LOOKBACK = MEDIUM_LOOKBACK
    LONG_LOOKBACK = LONG_LOOKBACK

    VOLATILITY_LOOKBACK = VOLATILITY_LOOKBACK

    # =========================================================================
    # VALIDATION
    # =========================================================================

    @staticmethod
    def _validate(
        candles: list[MarketCandle],
    ) -> None:

        if candles is None:
            raise ValueError(
                "candles cannot be None."
            )

        for index, candle in enumerate(candles):

            if candle is None:
                raise ValueError(
                    f"candle[{index}] cannot be None."
                )

            if candle.high < candle.low:
                raise ValueError(
                    f"candle[{index}] has high < low."
                )

            if candle.close <= 0:
                raise ValueError(
                    "Momentum analysis requires positive closing prices."
                )

    # =========================================================================
    # RETURN
    # =========================================================================

    @staticmethod
    def _return(
        prices: list[float],
        lookback: int,
    ) -> float:

        if len(prices) <= lookback:
            return 0.0

        previous = prices[-1 - lookback]

        if abs(previous) <= EPSILON:
            return 0.0

        return (
            (prices[-1] - previous)
            / abs(previous)
        ) * 100.0

    # =========================================================================
    # VOLATILITY
    # =========================================================================

    @classmethod
    def _volatility(
        cls,
        candles: list[MarketCandle],
    ) -> float:

        if len(candles) < 2:
            return 0.0

        start = max(
            1,
            len(candles) - cls.VOLATILITY_LOOKBACK,
        )

        returns: list[float] = []

        for index in range(
            start,
            len(candles),
        ):

            previous_close = candles[
                index - 1
            ].close

            current_close = candles[
                index
            ].close

            if abs(previous_close) <= EPSILON:
                continue

            returns.append(
                abs(
                    (
                        current_close
                        - previous_close
                    )
                    / previous_close
                )
                * 100.0
            )

        if not returns:
            return 0.0

        return sum(returns) / len(returns)

    # =========================================================================
    # NORMALIZATION
    # =========================================================================

    @staticmethod
    def _normalize(
        value: float,
        volatility: float,
    ) -> float:

        if volatility <= EPSILON:
            return 0.0

        return value / volatility

    # =========================================================================
    # PERSISTENCE
    # =========================================================================

    @staticmethod
    def _persistence(
        prices: list[float],
        lookback: int,
    ) -> float:

        if len(prices) < lookback + 1:
            return 0.0

        start = len(prices) - lookback

        bullish = 0
        bearish = 0
        total = 0

        for index in range(
            start,
            len(prices),
        ):

            change = (
                prices[index]
                - prices[index - 1]
            )

            if change > 0:
                bullish += 1

            elif change < 0:
                bearish += 1

            total += 1

        if total == 0:
            return 0.0

        directional = max(
            bullish,
            bearish,
        )

        return (
            directional / total
        ) * 100.0

    # =========================================================================
    # ACCELERATION
    # =========================================================================

    @staticmethod
    def _acceleration(
        prices: list[float],
    ) -> float:

        if len(prices) < 10:
            return 0.0

        recent = (
            prices[-1]
            - prices[-6]
        )

        previous = (
            prices[-6]
            - prices[-10]
        )

        return recent - previous

    # =========================================================================
    # ANALYSIS
    # =========================================================================

    def analyze(
        self,
        candles: list[MarketCandle],
    ) -> MomentumAnalysis:

        self._validate(candles)

        if len(candles) < self.MINIMUM_CANDLES:

            return MomentumAnalysis(
                velocity=0.0,
                acceleration=0.0,
                bullish=False,
                bearish=False,
                confidence=0.0,
            )

        closes = [
            float(candle.close)
            for candle in candles
        ]

        current_price = closes[-1]

        # ---------------------------------------------------------------------
        # Multi-horizon returns
        # ---------------------------------------------------------------------

        short_velocity = self._return(
            closes,
            self.SHORT_LOOKBACK,
        )

        medium_velocity = self._return(
            closes,
            self.MEDIUM_LOOKBACK,
        )

        long_velocity = self._return(
            closes,
            self.LONG_LOOKBACK,
        )

        # ---------------------------------------------------------------------
        # Legacy velocity
        #
        # Preserve the original meaning:
        # current close - close six candles ago.
        # ---------------------------------------------------------------------

        velocity = (
            closes[-1]
            - closes[-6]
        )

        acceleration = self._acceleration(
            closes
        )

        # ---------------------------------------------------------------------
        # Volatility normalization
        # ---------------------------------------------------------------------

        volatility = self._volatility(
            candles
        )

        normalized_velocity = self._normalize(
            medium_velocity,
            volatility,
        )

        acceleration_percent = 0.0

        base_price = closes[-6]

        if abs(base_price) > EPSILON:

            acceleration_percent = (
                acceleration
                / abs(base_price)
            ) * 100.0

        normalized_acceleration = self._normalize(
            acceleration_percent,
            volatility,
        )

        # ---------------------------------------------------------------------
        # Direction
        # ---------------------------------------------------------------------

        bullish = (
            short_velocity > 0
            and medium_velocity > 0
        )

        bearish = (
            short_velocity < 0
            and medium_velocity < 0
        )

        # ---------------------------------------------------------------------
        # Persistence
        # ---------------------------------------------------------------------

        persistence = self._persistence(
            closes,
            self.MEDIUM_LOOKBACK,
        )

        # ---------------------------------------------------------------------
        # Directional score
        #
        # Positive = bullish
        # Negative = bearish
        # Near zero = mixed.
        # ---------------------------------------------------------------------

        directional_score = (
            short_velocity * 0.35
            + medium_velocity * 0.40
            + long_velocity * 0.25
        )

        # ---------------------------------------------------------------------
        # Momentum strength
        # ---------------------------------------------------------------------

        normalized_strength = min(
            abs(normalized_velocity) * 20.0,
            100.0,
        )

        persistence_strength = (
            persistence * 0.30
        )

        strength = min(
            normalized_strength * 0.70
            + persistence_strength,
            100.0,
        )

        # ---------------------------------------------------------------------
        # Acceleration confirmation
        # ---------------------------------------------------------------------

        acceleration_bonus = min(
            abs(normalized_acceleration) * 10.0,
            15.0,
        )

        if (
            normalized_velocity > 0
            and normalized_acceleration > 0
        ):

            strength += acceleration_bonus

        elif (
            normalized_velocity < 0
            and normalized_acceleration < 0
        ):

            strength += acceleration_bonus

        strength = min(
            max(strength, 0.0),
            100.0,
        )

        # ---------------------------------------------------------------------
        # Exhaustion
        #
        # Strong momentum combined with weakening acceleration can indicate
        # exhaustion rather than continuation.
        # ---------------------------------------------------------------------

        exhaustion = False

        if abs(normalized_velocity) > 2.0:

            if (
                normalized_velocity > 0
                and normalized_acceleration < 0
            ):
                exhaustion = True

            elif (
                normalized_velocity < 0
                and normalized_acceleration > 0
            ):
                exhaustion = True

        # ---------------------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------------------

        confidence = strength

        if bullish or bearish:
            confidence += 10.0

        if persistence >= 70.0:
            confidence += 5.0

        if exhaustion:
            confidence -= 15.0

        confidence = min(
            max(confidence, 0.0),
            100.0,
        )

        confidence = round(
            confidence,
            2,
        )

        # ---------------------------------------------------------------------
        # Chart annotations
        # ---------------------------------------------------------------------

        annotations = [

            {
                "type": "MOMENTUM",
                "velocity": velocity,
                "normalized_velocity": normalized_velocity,
                "acceleration": acceleration,
                "normalized_acceleration": (
                    normalized_acceleration
                ),
                "strength": round(
                    strength,
                    2,
                ),
                "confidence": confidence,
                "bullish": bullish,
                "bearish": bearish,
                "exhaustion": exhaustion,
                "locked": True,
                "source": "trend.momentum",
            },

        ]

        return MomentumAnalysis(

            # -----------------------------------------------------------------
            # Compatibility fields
            # -----------------------------------------------------------------

            velocity=velocity,

            acceleration=acceleration,

            bullish=bullish,

            bearish=bearish,

            confidence=confidence,

            # -----------------------------------------------------------------
            # Extended intelligence
            # -----------------------------------------------------------------

            short_velocity=short_velocity,

            medium_velocity=medium_velocity,

            long_velocity=long_velocity,

            normalized_velocity=normalized_velocity,

            normalized_acceleration=(
                normalized_acceleration
            ),

            persistence=round(
                persistence,
                2,
            ),

            strength=round(
                strength,
                2,
            ),

            exhaustion=exhaustion,

            volatility=round(
                volatility,
                6,
            ),

            directional_score=round(
                directional_score,
                6,
            ),

            annotations=annotations,
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

momentum_engine = MomentumEngine()
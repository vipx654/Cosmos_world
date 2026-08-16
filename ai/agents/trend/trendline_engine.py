"""
===============================================================================
COSMOS Trendline Intelligence Engine
===============================================================================

Production-grade swing-derived trendline analysis.

Responsibilities
----------------
- Detect bullish and bearish structural trendlines
- Validate multi-touch trendlines
- Calculate normalized slope
- Measure trendline quality
- Measure structural consistency
- Detect potential breakout / breakdown conditions
- Produce chart annotation payloads
- Preserve the existing TrendlineAnalysis interface

Design principles
-----------------
- Deterministic
- Price-scale independent where possible
- Uses confirmed swing points only
- No standalone trading signal
- No API dependency
- Downstream-agent compatible

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import SwingPoint
from ai.models import SwingType


# =============================================================================
# CONSTANTS
# =============================================================================

MIN_TRENDLINE_POINTS = 2

TOUCH_TOLERANCE_PERCENT = 0.15

STRONG_TOUCH_COUNT = 3

MAX_BREAKOUT_DISTANCE_PERCENT = 0.50


# =============================================================================
# MODEL
# =============================================================================


@dataclass(slots=True)
class TrendlineAnalysis:
    """
    Complete trendline intelligence.

    Existing fields are preserved for compatibility.
    """

    bullish_trendline: bool

    bearish_trendline: bool

    slope: float

    touches: int

    confidence: float

    # -------------------------------------------------------------------------
    # Extended intelligence
    # -------------------------------------------------------------------------

    bullish_slope: float = 0.0

    bearish_slope: float = 0.0

    bullish_touches: int = 0

    bearish_touches: int = 0

    bullish_quality: float = 0.0

    bearish_quality: float = 0.0

    bullish_consistency: float = 0.0

    bearish_consistency: float = 0.0

    normalized_slope: float = 0.0

    breakout: bool = False

    breakdown: bool = False

    regime: str = "NEUTRAL"

    annotations: list[dict] | None = None


# =============================================================================
# ENGINE
# =============================================================================


class TrendlineEngine:
    """
    Production-grade trendline intelligence engine.

    Trendlines are confirmation evidence only.

    They must NEVER independently authorize a trade.
    """

    MIN_TRENDLINE_POINTS = MIN_TRENDLINE_POINTS

    TOUCH_TOLERANCE_PERCENT = (
        TOUCH_TOLERANCE_PERCENT
    )

    STRONG_TOUCH_COUNT = STRONG_TOUCH_COUNT

    # =========================================================================
    # VALIDATION
    # =========================================================================

    @staticmethod
    def _normalize_swings(
        swings: list[SwingPoint],
    ) -> list[SwingPoint]:

        if swings is None:
            return []

        valid = [

            swing

            for swing in swings

            if isinstance(
                swing,
                SwingPoint,
            )

            and swing.swing_type in (
                SwingType.HIGH,
                SwingType.LOW,
            )

        ]

        return sorted(
            valid,
            key=lambda swing: (
                swing.index,
                swing.timestamp,
            ),
        )

    # =========================================================================
    # LINE
    # =========================================================================

    @staticmethod
    def _line(
        p1: SwingPoint,
        p2: SwingPoint,
    ) -> tuple[float, float] | None:

        dx = p2.index - p1.index

        if dx == 0:
            return None

        slope = (
            p2.price - p1.price
        ) / dx

        intercept = (
            p1.price
            - slope * p1.index
        )

        return (
            slope,
            intercept,
        )

    # =========================================================================
    # LINE VALUE
    # =========================================================================

    @staticmethod
    def _value(
        slope: float,
        intercept: float,
        index: int,
    ) -> float:

        return (
            slope * index
            + intercept
        )

    # =========================================================================
    # TOUCH TOLERANCE
    # =========================================================================

    @classmethod
    def _is_touch(
        cls,
        price: float,
        line_price: float,
    ) -> bool:

        if line_price == 0:
            return abs(
                price - line_price
            ) <= 1e-12

        distance_percent = (
            abs(price - line_price)
            / abs(line_price)
        ) * 100.0

        return (
            distance_percent
            <= cls.TOUCH_TOLERANCE_PERCENT
        )

    # =========================================================================
    # TOUCHES
    # =========================================================================

    @classmethod
    def _count_touches(
        cls,
        points: list[SwingPoint],
        slope: float,
        intercept: float,
    ) -> tuple[int, float]:

        if not points:
            return 0, 0.0

        touches = 0
        errors: list[float] = []

        for point in points:

            expected = cls._value(
                slope,
                intercept,
                point.index,
            )

            if expected == 0:
                continue

            error = (
                abs(point.price - expected)
                / abs(expected)
            ) * 100.0

            errors.append(error)

            if cls._is_touch(
                point.price,
                expected,
            ):
                touches += 1

        if not errors:
            return touches, 0.0

        average_error = (
            sum(errors)
            / len(errors)
        )

        consistency = max(
            0.0,
            min(
                100.0,
                100.0
                - (
                    average_error
                    / cls.TOUCH_TOLERANCE_PERCENT
                    * 100.0
                ),
            ),
        )

        return (
            touches,
            consistency,
        )

    # =========================================================================
    # QUALITY
    # =========================================================================

    @classmethod
    def _quality(
        cls,
        touches: int,
        consistency: float,
    ) -> float:

        if touches < cls.MIN_TRENDLINE_POINTS:
            return 0.0

        touch_score = min(
            60.0,
            touches * 20.0,
        )

        quality = (
            touch_score
            + consistency * 0.40
        )

        return round(
            min(
                quality,
                100.0,
            ),
            2,
        )

    # =========================================================================
    # NORMALIZED SLOPE
    # =========================================================================

    @staticmethod
    def _normalized_slope(
        slope: float,
        price: float,
    ) -> float:

        if abs(price) <= 1e-12:
            return 0.0

        return (
            slope
            / abs(price)
        ) * 100.0

    # =========================================================================
    # ANALYSIS
    # =========================================================================

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> TrendlineAnalysis:

        normalized = self._normalize_swings(
            swings
        )

        highs = [
            swing
            for swing in normalized
            if swing.swing_type
            == SwingType.HIGH
        ]

        lows = [
            swing
            for swing in normalized
            if swing.swing_type
            == SwingType.LOW
        ]

        bullish = False
        bearish = False

        bullish_slope = 0.0
        bearish_slope = 0.0

        bullish_touches = 0
        bearish_touches = 0

        bullish_consistency = 0.0
        bearish_consistency = 0.0

        bullish_quality = 0.0
        bearish_quality = 0.0

        # =====================================================================
        # BULLISH TRENDLINE
        # =====================================================================

        if len(lows) >= MIN_TRENDLINE_POINTS:

            p1 = lows[-2]
            p2 = lows[-1]

            line = self._line(
                p1,
                p2,
            )

            if line is not None:

                slope, intercept = line

                bullish_slope = slope

                (
                    bullish_touches,
                    bullish_consistency,
                ) = self._count_touches(
                    lows,
                    slope,
                    intercept,
                )

                bullish_quality = self._quality(
                    bullish_touches,
                    bullish_consistency,
                )

                bullish = (
                    slope > 0
                    and bullish_touches >= 2
                )

        # =====================================================================
        # BEARISH TRENDLINE
        # =====================================================================

        if len(highs) >= MIN_TRENDLINE_POINTS:

            p1 = highs[-2]
            p2 = highs[-1]

            line = self._line(
                p1,
                p2,
            )

            if line is not None:

                slope, intercept = line

                bearish_slope = slope

                (
                    bearish_touches,
                    bearish_consistency,
                ) = self._count_touches(
                    highs,
                    slope,
                    intercept,
                )

                bearish_quality = self._quality(
                    bearish_touches,
                    bearish_consistency,
                )

                bearish = (
                    slope < 0
                    and bearish_touches >= 2
                )

        # =====================================================================
        # SELECT PRIMARY TRENDLINE
        # =====================================================================

        if bullish_quality > bearish_quality:

            slope = bullish_slope
            touches = bullish_touches
            confidence = bullish_quality
            regime = "BULLISH"

        elif bearish_quality > bullish_quality:

            slope = bearish_slope
            touches = bearish_touches
            confidence = bearish_quality
            regime = "BEARISH"

        else:

            slope = 0.0
            touches = max(
                bullish_touches,
                bearish_touches,
            )

            confidence = max(
                bullish_quality,
                bearish_quality,
            )

            regime = "NEUTRAL"

        # =====================================================================
        # NORMALIZED SLOPE
        # =====================================================================

        reference_price = 0.0

        if normalized:

            reference_price = normalized[-1].price

        normalized_slope = (
            self._normalized_slope(
                slope,
                reference_price,
            )
        )

        # =====================================================================
        # BREAKOUT / BREAKDOWN
        #
        # These are contextual observations only.
        # A final breakout decision belongs to dedicated structure engines.
        # =====================================================================

        breakout = False
        breakdown = False

        if bullish and lows:

            last_low = lows[-1]

            if bullish_slope > 0:

                expected = (
                    bullish_slope
                    * last_low.index
                    + (
                        last_low.price
                        - bullish_slope
                        * lows[-2].index
                    )
                )

                distance = (
                    abs(last_low.price - expected)
                    / max(
                        abs(expected),
                        1e-12,
                    )
                ) * 100.0

                if distance > MAX_BREAKOUT_DISTANCE_PERCENT:
                    breakout = True

        if bearish and highs:

            last_high = highs[-1]

            if bearish_slope < 0:

                expected = (
                    bearish_slope
                    * last_high.index
                    + (
                        last_high.price
                        - bearish_slope
                        * highs[-2].index
                    )
                )

                distance = (
                    abs(last_high.price - expected)
                    / max(
                        abs(expected),
                        1e-12,
                    )
                ) * 100.0

                if distance > MAX_BREAKOUT_DISTANCE_PERCENT:
                    breakdown = True

        # =====================================================================
        # CHART ANNOTATIONS
        # =====================================================================

        annotations = []

        if bullish:

            annotations.append(
                {
                    "type": "TRENDLINE",
                    "direction": "BULLISH",
                    "slope": bullish_slope,
                    "touches": bullish_touches,
                    "quality": bullish_quality,
                    "consistency": bullish_consistency,
                    "locked": True,
                    "source": "trend.trendline",
                }
            )

        if bearish:

            annotations.append(
                {
                    "type": "TRENDLINE",
                    "direction": "BEARISH",
                    "slope": bearish_slope,
                    "touches": bearish_touches,
                    "quality": bearish_quality,
                    "consistency": bearish_consistency,
                    "locked": True,
                    "source": "trend.trendline",
                }
            )

        return TrendlineAnalysis(

            # -----------------------------------------------------------------
            # Compatibility fields
            # -----------------------------------------------------------------

            bullish_trendline=bullish,

            bearish_trendline=bearish,

            slope=slope,

            touches=touches,

            confidence=confidence,

            # -----------------------------------------------------------------
            # Extended intelligence
            # -----------------------------------------------------------------

            bullish_slope=bullish_slope,

            bearish_slope=bearish_slope,

            bullish_touches=bullish_touches,

            bearish_touches=bearish_touches,

            bullish_quality=bullish_quality,

            bearish_quality=bearish_quality,

            bullish_consistency=round(
                bullish_consistency,
                2,
            ),

            bearish_consistency=round(
                bearish_consistency,
                2,
            ),

            normalized_slope=normalized_slope,

            breakout=breakout,

            breakdown=breakdown,

            regime=regime,

            annotations=annotations,
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

trendline_engine = TrendlineEngine()
"""
===============================================================================
COSMOS Bullish Fair Value Gap Engine V2

Production-grade bullish Fair Value Gap detection.

Responsibilities:

    - Detect three-candle bullish imbalance structures
    - Validate candle price data
    - Evaluate middle-candle displacement
    - Measure gap significance
    - Produce deterministic bounded quality scores
    - Generate structured evidence
    - Respect configured FVG limits

Detection model:

    Candle 1 High < Candle 3 Low

The resulting price region is:

    gap_low  = Candle 1 High
    gap_high = Candle 3 Low

The middle candle provides directional/displacement evidence.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

import math

from ai.agents.fvg.constants import (
    DEFAULT_CONFIDENCE,
    DEFAULT_DISPLACEMENT_SCORE,
    DEFAULT_PROBABILITY,
    DEFAULT_SOURCE,
    DEFAULT_STRENGTH,
    EXTREME_BODY_RATIO,
    EXTREME_GAP_RATIO,
    MAX_FVG_COUNT,
    MAX_SCORE,
    MIN_BODY_RATIO,
    MIN_GAP_RATIO,
    MIN_SCORE,
    SIGNIFICANT_GAP_RATIO,
    STRONG_BODY_RATIO,
    STRONG_DISPLACEMENT_SCORE,
    STRONG_GAP_RATIO,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGDirection,
    FVGStatus,
    FVGType,
)

from ai.agents.fvg.utils import (
    body_ratio,
    calculate_midpoint,
    candle_range,
    is_bullish_candle,
)


class BullishFVGEngine:
    """
    Detect bullish Fair Value Gaps.

    A bullish FVG exists when:

        Candle 1 High < Candle 3 Low

    The middle candle is evaluated for:

        - bullish direction
        - body quality
        - displacement
        - gap significance

    The engine is intentionally deterministic. It does not make trading
    decisions and does not depend on future agents such as:

        - Market Structure
        - Liquidity
        - Sweep
        - Order Block
        - SMC
        - Volume
        - Session
        - HTF confluence
    """

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        candles,
    ) -> list[FairValueGap]:
        """
        Detect bullish FVGs from an ordered candle collection.

        Returns:
            list[FairValueGap]

        Notes:
            The method preserves the existing COSMOS API:

                BullishFVGEngine().analyze(candles)

            Invalid individual candles are skipped rather than crashing the
            complete FVG pipeline.
        """

        fvgs: list[FairValueGap] = []

        # ---------------------------------------------------------------------
        # Basic input safety
        # ---------------------------------------------------------------------

        if candles is None:
            return fvgs

        try:
            candle_count = len(candles)
        except TypeError:
            return fvgs

        if candle_count < 3:
            return fvgs

        # ---------------------------------------------------------------------
        # Scan three-candle windows.
        # ---------------------------------------------------------------------

        for index in range(
            0,
            candle_count - 2,
        ):

            # Respect global FVG protection.
            if len(fvgs) >= MAX_FVG_COUNT:
                break

            first = candles[index]
            middle = candles[index + 1]
            third = candles[index + 2]

            # -----------------------------------------------------------------
            # Validate candle values.
            # -----------------------------------------------------------------

            first_values = self._extract_prices(first)

            middle_values = self._extract_prices(middle)

            third_values = self._extract_prices(third)

            if (
                first_values is None
                or middle_values is None
                or third_values is None
            ):
                continue

            (
                first_open,
                first_high,
                first_low,
                first_close,
            ) = first_values

            (
                middle_open,
                middle_high,
                middle_low,
                middle_close,
            ) = middle_values

            (
                third_open,
                third_high,
                third_low,
                third_close,
            ) = third_values

            # Keep local variables explicit for deterministic readability.
            _ = (
                first_open,
                first_close,
                third_open,
                third_high,
                third_close,
            )

            # -----------------------------------------------------------------
            # Candle ranges must be positive.
            # -----------------------------------------------------------------

            middle_range = (
                middle_high
                - middle_low
            )

            if middle_range <= 0.0:
                continue

            # -----------------------------------------------------------------
            # Bullish FVG structure.
            #
            # Candle 1 high must remain below Candle 3 low.
            # -----------------------------------------------------------------

            if first_high >= third_low:
                continue

            gap_low = first_high
            gap_high = third_low

            gap_size = (
                gap_high
                - gap_low
            )

            if gap_size <= 0.0:
                continue

            # -----------------------------------------------------------------
            # Gap quality.
            # -----------------------------------------------------------------

            gap_ratio = (
                gap_size
                /
                middle_range
            )

            if gap_ratio < MIN_GAP_RATIO:
                continue

            # -----------------------------------------------------------------
            # Middle candle quality.
            # -----------------------------------------------------------------

            middle_body_ratio = body_ratio(
                middle
            )

            middle_bullish = (
                middle_close
                >
                middle_open
            )

            # A weak middle candle is still allowed when its body is
            # sufficiently large. This preserves the original COSMOS
            # detection behavior while improving scoring.
            if (
                not middle_bullish
                and
                middle_body_ratio
                < MIN_BODY_RATIO
            ):
                continue

            # -----------------------------------------------------------------
            # Displacement score.
            # -----------------------------------------------------------------

            displacement_score = (
                self._calculate_displacement_score(
                    middle_body_ratio=middle_body_ratio,
                    gap_ratio=gap_ratio,
                    bullish=middle_bullish,
                )
            )

            # -----------------------------------------------------------------
            # Score the FVG.
            # -----------------------------------------------------------------

            confidence = float(
                DEFAULT_CONFIDENCE
            )

            probability = float(
                DEFAULT_PROBABILITY
            )

            strength = float(
                DEFAULT_STRENGTH
            )

            evidence: list[str] = [
                "Three Candle Imbalance",
                "Bullish FVG",
            ]

            # -----------------------------------------------------------------
            # Bullish middle candle.
            # -----------------------------------------------------------------

            if middle_bullish:
                confidence += 10.0
                probability += 10.0
                strength += 10.0

                evidence.append(
                    "Bullish Middle Candle"
                )

            # -----------------------------------------------------------------
            # Minimum body quality.
            # -----------------------------------------------------------------

            if (
                middle_body_ratio
                >= MIN_BODY_RATIO
            ):
                confidence += 5.0
                probability += 5.0
                strength += 5.0

                evidence.append(
                    "Strong Candle Body"
                )

            # -----------------------------------------------------------------
            # Strong body.
            # -----------------------------------------------------------------

            if (
                middle_body_ratio
                >= STRONG_BODY_RATIO
            ):
                confidence += 5.0
                probability += 5.0
                strength += 5.0

                evidence.append(
                    "Strong Displacement Body"
                )

            # -----------------------------------------------------------------
            # Extreme body.
            # -----------------------------------------------------------------

            if (
                middle_body_ratio
                >= EXTREME_BODY_RATIO
            ):
                confidence += 5.0
                probability += 5.0
                strength += 5.0

                evidence.append(
                    "Extreme Displacement Body"
                )

            # -----------------------------------------------------------------
            # Significant gap.
            # -----------------------------------------------------------------

            if (
                gap_ratio
                >= SIGNIFICANT_GAP_RATIO
            ):
                confidence += 10.0
                probability += 10.0
                strength += 10.0

                evidence.append(
                    "Significant Gap"
                )

            # -----------------------------------------------------------------
            # Strong gap.
            # -----------------------------------------------------------------

            if (
                gap_ratio
                >= STRONG_GAP_RATIO
            ):
                confidence += 5.0
                probability += 5.0
                strength += 5.0

                evidence.append(
                    "Strong Gap"
                )

            # -----------------------------------------------------------------
            # Extreme gap.
            # -----------------------------------------------------------------

            if (
                gap_ratio
                >= EXTREME_GAP_RATIO
            ):
                confidence += 5.0
                probability += 5.0
                strength += 5.0

                evidence.append(
                    "Extreme Gap"
                )

            # -----------------------------------------------------------------
            # Displacement quality.
            # -----------------------------------------------------------------

            if (
                displacement_score
                >= STRONG_DISPLACEMENT_SCORE
            ):
                confidence += 5.0
                probability += 5.0
                strength += 5.0

                evidence.append(
                    "Strong Displacement"
                )

            # -----------------------------------------------------------------
            # Bound scores.
            # -----------------------------------------------------------------

            confidence = self._clamp_score(
                confidence
            )

            probability = self._clamp_score(
                probability
            )

            strength = self._clamp_score(
                strength
            )

            # -----------------------------------------------------------------
            # Midpoint.
            # -----------------------------------------------------------------

            midpoint = calculate_midpoint(
                gap_low,
                gap_high,
            )

            # -----------------------------------------------------------------
            # Build FVG.
            # -----------------------------------------------------------------

            fvg = FairValueGap(
                fvg_type=FVGType.BULLISH,

                status=FVGStatus.FRESH,

                direction=FVGDirection.BULLISH,

                high=gap_high,

                low=gap_low,

                first_candle_index=index,

                middle_candle_index=index + 1,

                third_candle_index=index + 2,

                confidence=confidence,

                probability=probability,

                strength=strength,

                midpoint=midpoint,

                source=DEFAULT_SOURCE,

                evidence=evidence,
            )

            fvgs.append(
                fvg
            )

        return fvgs

    # =========================================================================
    # CANDLE VALIDATION
    # =========================================================================

    @staticmethod
    def _extract_prices(
        candle,
    ) -> tuple[float, float, float, float] | None:
        """
        Safely extract OHLC values from a candle.

        Returns:
            (open, high, low, close)

        Invalid, non-finite or structurally impossible candles return None.
        """

        try:
            open_price = float(
                candle.open
            )

            high = float(
                candle.high
            )

            low = float(
                candle.low
            )

            close = float(
                candle.close
            )

        except (
            AttributeError,
            TypeError,
            ValueError,
        ):
            return None

        # ---------------------------------------------------------------------
        # Reject NaN / infinity.
        # ---------------------------------------------------------------------

        if not all(
            math.isfinite(value)
            for value in (
                open_price,
                high,
                low,
                close,
            )
        ):
            return None

        # ---------------------------------------------------------------------
        # OHLC structural validation.
        # ---------------------------------------------------------------------

        if high < low:
            return None

        if open_price < low or open_price > high:
            return None

        if close < low or close > high:
            return None

        return (
            open_price,
            high,
            low,
            close,
        )

    # =========================================================================
    # DISPLACEMENT
    # =========================================================================

    @staticmethod
    def _calculate_displacement_score(
        middle_body_ratio: float,
        gap_ratio: float,
        bullish: bool,
    ) -> float:
        """
        Calculate deterministic displacement quality.

        This is a quality score, NOT a probability or win rate.

        Inputs are normalized into a 0-100 score.
        """

        body_component = min(
            100.0,
            max(
                0.0,
                middle_body_ratio * 100.0,
            ),
        )

        gap_component = min(
            100.0,
            max(
                0.0,
                gap_ratio * 100.0,
            ),
        )

        directional_component = (
            100.0
            if bullish
            else 50.0
        )

        score = (
            body_component * 0.45
            +
            gap_component * 0.35
            +
            directional_component * 0.20
        )

        # Preserve configured baseline semantics.
        if score <= 0.0:
            score = DEFAULT_DISPLACEMENT_SCORE

        return min(
            100.0,
            max(
                0.0,
                score,
            ),
        )

    # =========================================================================
    # SCORE HELPERS
    # =========================================================================

    @staticmethod
    def _clamp_score(
        value: float,
    ) -> float:
        """
        Clamp a score to the COSMOS global score range.
        """

        return round(
            min(
                MAX_SCORE,
                max(
                    MIN_SCORE,
                    float(value),
                ),
            ),
            2,
        )
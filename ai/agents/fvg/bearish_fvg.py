"""
===============================================================================
COSMOS Bearish Fair Value Gap Engine V2

Production-grade deterministic detector for bearish Fair Value Gaps.

Detection model:

    Candle 1 low > Candle 3 high

The resulting imbalance is:

    gap_low  = Candle 3 high
    gap_high = Candle 1 low

The middle candle is evaluated for bearish displacement quality.

Design goals:

    - Deterministic detection
    - Symmetric bullish/bearish behavior
    - Bounded confidence/probability/strength scores
    - Robust candle validation
    - Gap-size quality measurement
    - Displacement evidence
    - Stable FairValueGap contract
    - No downstream lifecycle logic
    - Compatible with the existing FVG pipeline

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

import math

from ai.agents.fvg.constants import (
    DEFAULT_CONFIDENCE,
    DEFAULT_PROBABILITY,
    DEFAULT_SOURCE,
    DEFAULT_STRENGTH,
    MAX_FVG_COUNT,
    MAX_SCORE,
    MIN_BODY_RATIO,
    MIN_FINITE_PRICE,
    SIGNIFICANT_GAP_RATIO,
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
    is_bearish_candle,
)


class BearishFVGEngine:
    """
    Detect bearish Fair Value Gaps using a three-candle imbalance structure.

    A bearish FVG exists when:

        Candle 1 low > Candle 3 high

    Therefore:

        gap_low  = Candle 3 high
        gap_high = Candle 1 low

    The middle candle is expected to demonstrate bearish displacement.
    """

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        candles,
    ) -> list[FairValueGap]:
        """
        Detect all valid bearish FVGs in the supplied candle sequence.

        The detector is intentionally state-free and deterministic.
        """

        if candles is None:
            return []

        try:
            candle_count = len(candles)
        except TypeError:
            return []

        if candle_count < 3:
            return []

        fvgs: list[FairValueGap] = []

        for index in range(
            candle_count - 2
        ):
            if len(fvgs) >= MAX_FVG_COUNT:
                break

            first = candles[index]
            middle = candles[index + 1]
            third = candles[index + 2]

            fvg = self._detect(
                first=first,
                middle=middle,
                third=third,
                index=index,
            )

            if fvg is not None:
                fvgs.append(fvg)

        return fvgs

    # =========================================================================
    # DETECTION
    # =========================================================================

    @classmethod
    def _detect(
        cls,
        first,
        middle,
        third,
        index: int,
    ) -> FairValueGap | None:
        """
        Detect one bearish FVG candidate.
        """

        # ---------------------------------------------------------------------
        # Validate candle prices.
        # ---------------------------------------------------------------------

        first_low = cls._finite_price(
            getattr(first, "low", None)
        )

        third_high = cls._finite_price(
            getattr(third, "high", None)
        )

        if first_low is None or third_high is None:
            return None

        # ---------------------------------------------------------------------
        # Bearish FVG structure.
        #
        # Candle 1 low must remain above Candle 3 high.
        # ---------------------------------------------------------------------

        if first_low <= third_high:
            return None

        gap_low = third_high
        gap_high = first_low

        gap_size = gap_high - gap_low

        if gap_size <= 0:
            return None

        # ---------------------------------------------------------------------
        # Middle candle range.
        # ---------------------------------------------------------------------

        middle_range = candle_range(
            middle
        )

        if middle_range <= 0:
            return None

        middle_body_ratio = body_ratio(
            middle
        )

        bearish_middle = is_bearish_candle(
            middle
        )

        # ---------------------------------------------------------------------
        # Reject weak/non-directional middle candles.
        #
        # Preserve the existing engine's behavior:
        #
        #   bearish candle
        #       OR
        #   sufficiently large body
        #
        # This keeps compatibility with the existing test contract.
        # ---------------------------------------------------------------------

        if (
            not bearish_middle
            and middle_body_ratio < MIN_BODY_RATIO
        ):
            return None

        # ---------------------------------------------------------------------
        # Gap significance.
        # ---------------------------------------------------------------------

        gap_ratio = (
            gap_size / middle_range
        )

        # ---------------------------------------------------------------------
        # Initial scores.
        # ---------------------------------------------------------------------

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
            "Bearish FVG",
        ]

        # ---------------------------------------------------------------------
        # Bearish displacement quality.
        # ---------------------------------------------------------------------

        if (
            bearish_middle
            and middle_body_ratio >= MIN_BODY_RATIO
        ):
            confidence += 10.0
            probability += 10.0
            strength += 10.0

            evidence.append(
                "Bearish Middle Candle"
            )

        # ---------------------------------------------------------------------
        # Significant imbalance.
        # ---------------------------------------------------------------------

        if gap_ratio >= SIGNIFICANT_GAP_RATIO:
            confidence += 10.0
            probability += 10.0
            strength += 10.0

            evidence.append(
                "Significant Gap"
            )

        # ---------------------------------------------------------------------
        # Strong displacement.
        #
        # This is additional evidence only when the middle candle has a
        # clearly directional body.
        # ---------------------------------------------------------------------

        if (
            bearish_middle
            and middle_body_ratio >= 0.65
        ):
            confidence += 5.0
            probability += 5.0
            strength += 5.0

            evidence.append(
                "Strong Bearish Displacement"
            )

        # ---------------------------------------------------------------------
        # Very strong displacement.
        # ---------------------------------------------------------------------

        if (
            bearish_middle
            and middle_body_ratio >= 0.80
        ):
            confidence += 5.0
            probability += 5.0
            strength += 5.0

            evidence.append(
                "Extreme Bearish Displacement"
            )

        # ---------------------------------------------------------------------
        # Bound all scores.
        # ---------------------------------------------------------------------

        confidence = cls._clamp_score(
            confidence
        )

        probability = cls._clamp_score(
            probability
        )

        strength = cls._clamp_score(
            strength
        )

        # ---------------------------------------------------------------------
        # Midpoint.
        # ---------------------------------------------------------------------

        midpoint = calculate_midpoint(
            gap_low,
            gap_high,
        )

        # ---------------------------------------------------------------------
        # Construct FVG.
        # ---------------------------------------------------------------------

        return FairValueGap(
            fvg_type=FVGType.BEARISH,

            status=FVGStatus.FRESH,

            direction=FVGDirection.BEARISH,

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

    # =========================================================================
    # VALIDATION HELPERS
    # =========================================================================

    @staticmethod
    def _finite_price(
        value,
    ) -> float | None:
        """
        Convert a price to float and reject invalid values.
        """

        try:
            price = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

        if not math.isfinite(price):
            return None

        if price < MIN_FINITE_PRICE:
            return None

        return price

    @staticmethod
    def _clamp_score(
        value: float,
    ) -> float:
        """
        Keep a score inside the global COSMOS score range.
        """

        return max(
            0.0,
            min(
                float(MAX_SCORE),
                float(value),
            ),
        )
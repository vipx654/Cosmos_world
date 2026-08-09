"""
===============================================================================
COSMOS Smart Money Confidence Engine

Combines Smart Money Concept engines into one
institutional confidence score.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.smc.constants import (
    WEIGHT_DEALING_RANGE,
    WEIGHT_PREMIUM_DISCOUNT,
    WEIGHT_FVG,
    WEIGHT_EQUAL_LEVELS,
    WEIGHT_INDUCEMENT,
)

from ai.agents.smc.models import (
    DealingRange,
    PremiumDiscount,
    FairValueGap,
    EqualLevel,
    Inducement,
    FVGType,
    ZoneType,
    InducementType,
)


class ConfidenceEngine:
    """
    Calculates the institutional confidence
    for Smart Money Concepts.
    """

    def calculate(
        self,
        dealing_range: DealingRange,
        premium_discount: PremiumDiscount,
        fvg: FairValueGap,
        equal_high: EqualLevel | None,
        equal_low: EqualLevel | None,
        inducement: Inducement,
    ) -> float:

        score = 0.0

        # ---------------------------------------------------------
        # Dealing Range
        # ---------------------------------------------------------

        if dealing_range.high > dealing_range.low:

            score += WEIGHT_DEALING_RANGE

        # ---------------------------------------------------------
        # Premium / Discount
        # ---------------------------------------------------------

        if premium_discount.zone != ZoneType.EQUILIBRIUM:

            score += WEIGHT_PREMIUM_DISCOUNT

        # ---------------------------------------------------------
        # Fair Value Gap
        # ---------------------------------------------------------

        if fvg.gap_type != FVGType.NONE:

            score += WEIGHT_FVG

        # ---------------------------------------------------------
        # Equal High / Low
        # ---------------------------------------------------------

        if equal_high is not None:

            score += WEIGHT_EQUAL_LEVELS / 2

        if equal_low is not None:

            score += WEIGHT_EQUAL_LEVELS / 2

        # ---------------------------------------------------------
        # Inducement
        # ---------------------------------------------------------

        if inducement.inducement_type != InducementType.NONE:

            score += WEIGHT_INDUCEMENT

        return round(

            min(score, 100.0),

            2,
        )
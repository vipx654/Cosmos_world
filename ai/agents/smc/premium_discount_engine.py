"""
===============================================================================
COSMOS Premium / Discount Engine

Institutional Premium & Discount calculation.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.smc.constants import (
    DISCOUNT_THRESHOLD,
    PREMIUM_THRESHOLD,
)

from ai.agents.smc.models import (
    DealingRange,
    PremiumDiscount,
    ZoneType,
)


class PremiumDiscountEngine:
    """
    Determines whether current price is trading
    in Premium, Discount or Equilibrium.
    """

    def analyze(
        self,
        price: float,
        dealing_range: DealingRange,
    ) -> PremiumDiscount:

        total_range = (
            dealing_range.high
            - dealing_range.low
        )

        if total_range <= 0:

            return PremiumDiscount(

                zone=ZoneType.EQUILIBRIUM,

                distance_from_eq=0.0,
            )

        position = (

            price
            -
            dealing_range.low

        ) / total_range

        zone = ZoneType.EQUILIBRIUM

        if position >= PREMIUM_THRESHOLD:

            zone = ZoneType.PREMIUM

        elif position <= DISCOUNT_THRESHOLD:

            zone = ZoneType.DISCOUNT

        distance = abs(

            price
            -
            dealing_range.equilibrium

        )

        return PremiumDiscount(

            zone=zone,

            distance_from_eq=round(
                distance,
                6,
            ),
        )
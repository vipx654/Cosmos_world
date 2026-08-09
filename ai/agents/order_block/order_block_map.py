"""
===============================================================================
COSMOS Order Block Map Engine

Builds the final organized Order Block map.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.order_block.models import (
    OrderBlock,
    OrderBlockMap,
    OrderBlockStatus,
    OrderBlockType,
)
from ai.agents.order_block.utils import (
    filter_bullish,
    filter_bearish,
    filter_fresh,
    filter_mitigated,
)


class OrderBlockMapEngine:
    """
    Organizes all detected order blocks into categories.

    V1 responsibilities:

    - Bullish blocks
    - Bearish blocks
    - Breakers
    - Mitigated blocks
    - Fresh blocks
    - Tested blocks
    - Invalid blocks
    - Complete block collection
    """

    def build(
        self,
        blocks: list[OrderBlock],
        breakers: list[OrderBlock],
    ) -> OrderBlockMap:

        # ---------------------------------------------------------------------
        # Combine original blocks and breaker blocks.
        # ---------------------------------------------------------------------

        all_blocks: list[OrderBlock] = []

        seen_ids: set[int] = set()

        for block in (
            blocks + breakers
        ):

            block_id = id(block)

            if block_id in seen_ids:
                continue

            seen_ids.add(block_id)

            all_blocks.append(block)

        # ---------------------------------------------------------------------
        # Direction
        # ---------------------------------------------------------------------

        bullish = filter_bullish(
            all_blocks
        )

        bearish = filter_bearish(
            all_blocks
        )

        # ---------------------------------------------------------------------
        # Breakers
        # ---------------------------------------------------------------------

        breaker_blocks = [

            block

            for block in all_blocks

            if (
                block.block_type
                == OrderBlockType.BREAKER
            )

            or block.breaker

        ]

        # ---------------------------------------------------------------------
        # Fresh
        # ---------------------------------------------------------------------

        fresh = filter_fresh(
            all_blocks
        )

        # ---------------------------------------------------------------------
        # Mitigated
        # ---------------------------------------------------------------------

        mitigated = filter_mitigated(
            all_blocks
        )

        # ---------------------------------------------------------------------
        # Tested
        # ---------------------------------------------------------------------

        tested = [

            block

            for block in all_blocks

            if (
                block.status
                == OrderBlockStatus.TESTED
            )

        ]

        # ---------------------------------------------------------------------
        # Invalid
        # ---------------------------------------------------------------------

        invalid = [

            block

            for block in all_blocks

            if (
                block.status
                == OrderBlockStatus.INVALID
            )

            or not block.valid

        ]

        return OrderBlockMap(

            bullish=bullish,

            bearish=bearish,

            breakers=breaker_blocks,

            mitigated=mitigated,

            fresh=fresh,

            tested=tested,

            invalid=invalid,

            all_blocks=all_blocks,

        )
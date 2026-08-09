"""
===============================================================================
COSMOS Order Block Mitigation Engine

Tracks whether price has tested or mitigated an order block.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.order_block.constants import (
    FULL_MITIGATION_RATIO,
    PARTIAL_MITIGATION_RATIO,
)

from ai.agents.order_block.models import (
    MitigationResult,
    MitigationStatus,
    OrderBlock,
    OrderBlockStatus,
)

from ai.agents.order_block.utils import (
    calculate_penetration,
    classify_mitigation,
)


class MitigationEngine:
    """
    Analyzes subsequent candles against detected order blocks.

    V1:

    - Detect touch
    - Detect partial penetration
    - Detect full mitigation
    - Track mitigation count
    - Invalidate a fully consumed block

    Advanced mitigation logic will be added later.
    """

    def analyze(
        self,
        blocks: list[OrderBlock],
        candles,
    ) -> list[MitigationResult]:

        results: list[MitigationResult] = []

        if not blocks or not candles:
            return results

        for block in blocks:

            touched = False

            fully_mitigated = False

            invalidated = False

            highest_penetration = 0.0

            evidence: list[str] = []

            # ---------------------------------------------------------------
            # Only inspect candles after the block was created.
            # ---------------------------------------------------------------

            start_index = (
                block.candle_index + 1
            )

            for index in range(
                start_index,
                len(candles),
            ):

                candle = candles[index]

                penetration = calculate_penetration(
                    candle,
                    block,
                )

                if penetration <= 0.0:
                    continue

                touched = True

                highest_penetration = max(
                    highest_penetration,
                    penetration,
                )

                block.mitigation_count += 1

                # -----------------------------------------------------------
                # Partial mitigation
                # -----------------------------------------------------------

                if penetration >= PARTIAL_MITIGATION_RATIO:

                    block.mitigation_status = (
                        MitigationStatus.PARTIAL
                    )

                    block.status = (
                        OrderBlockStatus.TESTED
                    )

                    evidence.append(
                        "Order Block Partially Mitigated"
                    )

                # -----------------------------------------------------------
                # Full mitigation
                # -----------------------------------------------------------

                if penetration >= FULL_MITIGATION_RATIO:

                    block.mitigation_status = (
                        MitigationStatus.FULL
                    )

                    block.status = (
                        OrderBlockStatus.MITIGATED
                    )

                    fully_mitigated = True

                    evidence.append(
                        "Order Block Fully Mitigated"
                    )

                    break

            # -----------------------------------------------------------------
            # No mitigation
            # -----------------------------------------------------------------

            if not touched:

                block.mitigation_status = (
                    MitigationStatus.UNTOUCHED
                )

                block.status = (
                    OrderBlockStatus.FRESH
                )

                evidence.append(
                    "Order Block Untouched"
                )

            # -----------------------------------------------------------------
            # Full mitigation invalidates the block for fresh entries.
            # -----------------------------------------------------------------

            if fully_mitigated:

                block.valid = False

                block.status = (
                    OrderBlockStatus.INVALID
                )

                block.mitigation_status = (
                    MitigationStatus.INVALIDATED
                )

                invalidated = True

                evidence.append(
                    "Order Block Invalidated"
                )

            status = classify_mitigation(
                highest_penetration
            )

            # -----------------------------------------------------------------
            # Preserve invalidation state.
            # -----------------------------------------------------------------

            if invalidated:

                status = (
                    MitigationStatus.INVALIDATED
                )

            results.append(
                MitigationResult(

                    order_block=block,

                    status=status,

                    penetration=round(
                        highest_penetration,
                        4,
                    ),

                    touched=touched,

                    fully_mitigated=(
                        fully_mitigated
                    ),

                    invalidated=(
                        invalidated
                    ),

                    evidence=evidence,
                )
            )

        return results
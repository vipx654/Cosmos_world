"""
===============================================================================
COSMOS Order Block Utilities

Shared helper functions for Order Block analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.order_block.models import (
    MitigationStatus,
    OrderBlock,
    OrderBlockDirection,
    OrderBlockStatus,
)


def candle_range(candle) -> float:
    """
    Return the full candle range.
    """

    return max(
        0.0,
        float(candle.high) - float(candle.low),
    )


def candle_body(candle) -> float:
    """
    Return the absolute candle body size.
    """

    return abs(
        float(candle.close)
        -
        float(candle.open)
    )


def body_ratio(candle) -> float:
    """
    Return candle body as a percentage of total range.

    Returns 0 when the candle has no range.
    """

    total_range = candle_range(candle)

    if total_range <= 0:
        return 0.0

    return candle_body(candle) / total_range


def is_bullish_candle(candle) -> bool:
    """
    Determine whether a candle closed above its open.
    """

    return (
        float(candle.close)
        >
        float(candle.open)
    )


def is_bearish_candle(candle) -> bool:
    """
    Determine whether a candle closed below its open.
    """

    return (
        float(candle.close)
        <
        float(candle.open)
    )


def midpoint(order_block: OrderBlock) -> float:
    """
    Return the midpoint of an order block.
    """

    return (
        float(order_block.high)
        +
        float(order_block.low)
    ) / 2.0


def block_range(order_block: OrderBlock) -> float:
    """
    Return the price range of an order block.
    """

    return max(
        0.0,
        float(order_block.high)
        -
        float(order_block.low),
    )


def price_inside_block(
    price: float,
    order_block: OrderBlock,
) -> bool:
    """
    Check whether a price is inside an order block.
    """

    return (
        float(order_block.low)
        <= float(price)
        <= float(order_block.high)
    )


def block_touched_by_candle(
    candle,
    order_block: OrderBlock,
) -> bool:
    """
    Check whether a candle touched an order block.
    """

    return (
        float(candle.high)
        >= float(order_block.low)
        and
        float(candle.low)
        <= float(order_block.high)
    )


def calculate_penetration(
    candle,
    order_block: OrderBlock,
) -> float:
    """
    Estimate how deeply a candle penetrated an order block.

    Returns a normalized value from 0.0 to 1.0.
    """

    total_range = block_range(
        order_block
    )

    if total_range <= 0:
        return 0.0

    candle_high = float(candle.high)
    candle_low = float(candle.low)

    block_high = float(order_block.high)
    block_low = float(order_block.low)

    if (
        candle_high < block_low
        or
        candle_low > block_high
    ):
        return 0.0

    overlap_high = min(
        candle_high,
        block_high,
    )

    overlap_low = max(
        candle_low,
        block_low,
    )

    overlap = max(
        0.0,
        overlap_high - overlap_low,
    )

    return min(
        1.0,
        overlap / total_range,
    )


def classify_mitigation(
    penetration: float,
) -> MitigationStatus:
    """
    Classify mitigation based on normalized penetration.
    """

    penetration = max(
        0.0,
        min(
            1.0,
            float(penetration),
        ),
    )

    if penetration <= 0.0:
        return MitigationStatus.UNTOUCHED

    if penetration < 0.50:
        return MitigationStatus.PARTIAL

    if penetration < 1.00:
        return MitigationStatus.PARTIAL

    return MitigationStatus.FULL


def strongest_order_block(
    blocks: list[OrderBlock],
) -> OrderBlock | None:
    """
    Return the strongest order block.
    """

    if not blocks:
        return None

    return max(
        blocks,
        key=lambda block: block.strength,
    )


def highest_confidence_block(
    blocks: list[OrderBlock],
) -> OrderBlock | None:
    """
    Return the block with the highest confidence.
    """

    if not blocks:
        return None

    return max(
        blocks,
        key=lambda block: block.confidence,
    )


def average_probability(
    blocks: list[OrderBlock],
) -> float:
    """
    Calculate average probability.
    """

    if not blocks:
        return 0.0

    return round(
        sum(
            block.probability
            for block in blocks
        )
        / len(blocks),
        2,
    )


def average_confidence(
    blocks: list[OrderBlock],
) -> float:
    """
    Calculate average confidence.
    """

    if not blocks:
        return 0.0

    return round(
        sum(
            block.confidence
            for block in blocks
        )
        / len(blocks),
        2,
    )


def filter_bullish(
    blocks: list[OrderBlock],
) -> list[OrderBlock]:
    """
    Return bullish order blocks.
    """

    return [
        block
        for block in blocks
        if block.direction
        == OrderBlockDirection.BULLISH
    ]


def filter_bearish(
    blocks: list[OrderBlock],
) -> list[OrderBlock]:
    """
    Return bearish order blocks.
    """

    return [
        block
        for block in blocks
        if block.direction
        == OrderBlockDirection.BEARISH
    ]


def filter_fresh(
    blocks: list[OrderBlock],
) -> list[OrderBlock]:
    """
    Return fresh order blocks.
    """

    return [
        block
        for block in blocks
        if block.status
        == OrderBlockStatus.FRESH
    ]


def filter_mitigated(
    blocks: list[OrderBlock],
) -> list[OrderBlock]:
    """
    Return mitigated order blocks.
    """

    return [
        block
        for block in blocks
        if block.status
        == OrderBlockStatus.MITIGATED
        or
        block.mitigation_status
        == MitigationStatus.FULL
    ]
"""
===============================================================================
COSMOS Order Block Agent Tests

Production validation tests for Order Block Agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from ai.agents.order_block.bearish_order_block import (
    BearishOrderBlockEngine,
)

from ai.agents.order_block.breaker_engine import (
    BreakerEngine,
)

from ai.agents.order_block.bullish_order_block import (
    BullishOrderBlockEngine,
)

from ai.agents.order_block.confidence_engine import (
    ConfidenceEngine,
)

from ai.agents.order_block.confirmation_engine import (
    ConfirmationEngine,
)

from ai.agents.order_block.constants import (
    MIN_CANDLES_REQUIRED,
)

from ai.agents.order_block.mitigation_engine import (
    MitigationEngine,
)

from ai.agents.order_block.models import (
    MitigationStatus,
    OrderBlock,
    OrderBlockDirection,
    OrderBlockStatus,
    OrderBlockType,
)

from ai.agents.order_block.order_block_map import (
    OrderBlockMapEngine,
)

from ai.agents.order_block.probability_engine import (
    ProbabilityEngine,
)

from ai.agents.order_block.utils import (
    average_confidence,
    average_probability,
    body_ratio,
    calculate_penetration,
    candle_body,
    candle_range,
    classify_mitigation,
    filter_bearish,
    filter_bullish,
    filter_fresh,
    filter_mitigated,
    is_bearish_candle,
    is_bullish_candle,
    midpoint,
    price_inside_block,
    strongest_order_block,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================


@dataclass(slots=True)
class TestCandle:
    """
    Minimal candle model used by Order Block tests.
    """

    open: float
    high: float
    low: float
    close: float
    time: int = 0


def candle(
    open_price: float,
    high: float,
    low: float,
    close: float,
    time: int = 0,
) -> TestCandle:
    """
    Create a test candle.
    """

    return TestCandle(
        open=open_price,
        high=high,
        low=low,
        close=close,
        time=time,
    )


def bullish_candle() -> TestCandle:
    """
    Strong bullish candle.
    """

    return candle(
        open_price=100.0,
        high=105.0,
        low=99.0,
        close=104.0,
    )


def bearish_candle() -> TestCandle:
    """
    Strong bearish candle.
    """

    return candle(
        open_price=104.0,
        high=105.0,
        low=99.0,
        close=100.0,
    )


def bullish_order_block() -> OrderBlock:
    """
    Create a valid bullish order block.
    """

    return OrderBlock(
        block_type=OrderBlockType.BULLISH,
        status=OrderBlockStatus.FRESH,
        direction=OrderBlockDirection.BULLISH,
        high=105.0,
        low=100.0,
        candle_index=1,
        confidence=80.0,
        probability=80.0,
        strength=80.0,
        valid=True,
    )


def bearish_order_block() -> OrderBlock:
    """
    Create a valid bearish order block.
    """

    return OrderBlock(
        block_type=OrderBlockType.BEARISH,
        status=OrderBlockStatus.FRESH,
        direction=OrderBlockDirection.BEARISH,
        high=105.0,
        low=100.0,
        candle_index=1,
        confidence=80.0,
        probability=80.0,
        strength=80.0,
        valid=True,
    )


# =============================================================================
# UTILITY TESTS
# =============================================================================


def test_candle_range():

    test_candle = candle(
        100.0,
        110.0,
        95.0,
        105.0,
    )

    assert candle_range(
        test_candle
    ) == 15.0


def test_candle_body():

    test_candle = candle(
        100.0,
        110.0,
        95.0,
        106.0,
    )

    assert candle_body(
        test_candle
    ) == 6.0


def test_body_ratio():

    test_candle = candle(
        100.0,
        110.0,
        95.0,
        106.0,
    )

    assert body_ratio(
        test_candle
    ) == pytest.approx(
        6.0 / 15.0
    )


def test_bullish_and_bearish_candle_detection():

    assert is_bullish_candle(
        bullish_candle()
    )

    assert is_bearish_candle(
        bearish_candle()
    )


def test_order_block_midpoint():

    block = bullish_order_block()

    assert midpoint(
        block
    ) == 102.5


def test_price_inside_order_block():

    block = bullish_order_block()

    assert price_inside_block(
        102.5,
        block,
    )

    assert not price_inside_block(
        110.0,
        block,
    )


def test_calculate_penetration():

    block = bullish_order_block()

    test_candle = candle(
        102.0,
        104.0,
        101.0,
        103.0,
    )

    penetration = calculate_penetration(
        test_candle,
        block,
    )

    assert penetration == pytest.approx(
        3.0 / 5.0
    )


def test_classify_mitigation():

    assert (
        classify_mitigation(0.0)
        == MitigationStatus.UNTOUCHED
    )

    assert (
        classify_mitigation(0.25)
        == MitigationStatus.PARTIAL
    )

    assert (
        classify_mitigation(1.0)
        == MitigationStatus.FULL
    )


# =============================================================================
# BULLISH ORDER BLOCK TESTS
# =============================================================================


def test_bullish_order_block_detection():

    candles = [

        candle(
            100.0,
            101.0,
            99.0,
            100.5,
        ),

        candle(
            105.0,
            106.0,
            99.0,
            100.0,
        ),

        candle(
            100.0,
            110.0,
            99.0,
            108.0,
        ),

    ]

    engine = (
        BullishOrderBlockEngine()
    )

    blocks = engine.analyze(
        candles
    )

    assert len(blocks) == 1

    block = blocks[0]

    assert (
        block.block_type
        == OrderBlockType.BULLISH
    )

    assert (
        block.direction
        == OrderBlockDirection.BULLISH
    )

    assert (
        block.status
        == OrderBlockStatus.FRESH
    )

    assert block.valid is True


def test_bullish_order_block_empty_for_insufficient_candles():

    candles = [

        candle(
            100.0,
            101.0,
            99.0,
            100.5,
        ),

        candle(
            100.0,
            102.0,
            99.0,
            101.0,
        ),

    ]

    engine = (
        BullishOrderBlockEngine()
    )

    assert engine.analyze(
        candles
    ) == []


# =============================================================================
# BEARISH ORDER BLOCK TESTS
# =============================================================================


def test_bearish_order_block_detection():

    candles = [

        candle(
            100.0,
            101.0,
            99.0,
            100.5,
        ),

        candle(
            100.0,
            106.0,
            99.0,
            105.0,
        ),

        candle(
            105.0,
            106.0,
            95.0,
            96.0,
        ),

    ]

    engine = (
        BearishOrderBlockEngine()
    )

    blocks = engine.analyze(
        candles
    )

    assert len(blocks) == 1

    block = blocks[0]

    assert (
        block.block_type
        == OrderBlockType.BEARISH
    )

    assert (
        block.direction
        == OrderBlockDirection.BEARISH
    )

    assert (
        block.status
        == OrderBlockStatus.FRESH
    )

    assert block.valid is True


def test_bearish_order_block_empty_for_insufficient_candles():

    candles = [

        candle(
            100.0,
            101.0,
            99.0,
            100.5,
        ),

        candle(
            100.0,
            102.0,
            99.0,
            101.0,
        ),

    ]

    engine = (
        BearishOrderBlockEngine()
    )

    assert engine.analyze(
        candles
    ) == []


# =============================================================================
# PROBABILITY TESTS
# =============================================================================


def test_probability_engine_calculates_bounded_probability():

    block = bullish_order_block()

    engine = ProbabilityEngine()

    result = engine.calculate(
        [block]
    )

    assert len(result) == 1

    assert 0.0 <= (
        result[0].probability
    ) <= 100.0

    assert (
        "Probability Calculated"
        in result[0].evidence
    )


def test_probability_engine_handles_empty_input():

    engine = ProbabilityEngine()

    assert engine.calculate(
        []
    ) == []


# =============================================================================
# CONFIDENCE TESTS
# =============================================================================


def test_confidence_engine_calculates_average():

    first = bullish_order_block()

    second = bearish_order_block()

    engine = ConfidenceEngine()

    confidence = engine.calculate(
        [first, second]
    )

    assert 0.0 <= confidence <= 100.0

    assert (
        "Confidence Calculated"
        in first.evidence
    )

    assert (
        "Confidence Calculated"
        in second.evidence
    )


def test_confidence_engine_empty_input():

    engine = ConfidenceEngine()

    assert (
        engine.calculate([])
        == 0.0
    )


# =============================================================================
# MITIGATION TESTS
# =============================================================================


def test_mitigation_engine_untouched_block():

    block = bullish_order_block()

    candles = [

        candle(
            110.0,
            115.0,
            108.0,
            112.0,
        ),

    ]

    engine = MitigationEngine()

    results = engine.analyze(
        [block],
        candles,
    )

    assert len(results) == 1

    result = results[0]

    assert result.touched is False

    assert (
        result.status
        == MitigationStatus.UNTOUCHED
    )

    assert (
        block.status
        == OrderBlockStatus.FRESH
    )


def test_mitigation_engine_partial_block():

    block = bullish_order_block()

    candles = [

        candle(
            102.0,
            104.0,
            101.0,
            103.0,
        ),

    ]

    engine = MitigationEngine()

    results = engine.analyze(
        [block],
        candles,
    )

    assert len(results) == 1

    result = results[0]

    assert result.touched is True

    assert result.penetration > 0.0

    assert (
        block.mitigation_status
        in (
            MitigationStatus.PARTIAL,
            MitigationStatus.FULL,
        )
    )


def test_mitigation_engine_full_invalidation():

    block = bullish_order_block()

    candles = [

        candle(
            103.0,
            108.0,
            97.0,
            99.0,
        ),

    ]

    engine = MitigationEngine()

    results = engine.analyze(
        [block],
        candles,
    )

    assert len(results) == 1

    result = results[0]

    assert result.touched is True

    assert result.fully_mitigated is True

    assert result.invalidated is True

    assert block.valid is False

    assert (
        block.status
        == OrderBlockStatus.INVALID
    )

    assert (
        block.mitigation_status
        == MitigationStatus.INVALIDATED
    )


# =============================================================================
# BREAKER TESTS
# =============================================================================


def test_bullish_invalid_block_becomes_bearish_breaker():

    block = bullish_order_block()

    block.valid = False

    engine = BreakerEngine()

    breakers = engine.analyze(
        [block]
    )

    assert len(breakers) == 1

    breaker = breakers[0]

    assert (
        breaker.block_type
        == OrderBlockType.BREAKER
    )

    assert (
        breaker.direction
        == OrderBlockDirection.BEARISH
    )

    assert breaker.breaker is True

    assert (
        breaker.status
        == OrderBlockStatus.TESTED
    )


def test_bearish_invalid_block_becomes_bullish_breaker():

    block = bearish_order_block()

    block.valid = False

    engine = BreakerEngine()

    breakers = engine.analyze(
        [block]
    )

    assert len(breakers) == 1

    breaker = breakers[0]

    assert (
        breaker.block_type
        == OrderBlockType.BREAKER
    )

    assert (
        breaker.direction
        == OrderBlockDirection.BULLISH
    )

    assert breaker.breaker is True


def test_existing_breaker_is_not_processed_twice():

    block = bullish_order_block()

    block.valid = False

    block.breaker = True

    block.block_type = (
        OrderBlockType.BREAKER
    )

    engine = BreakerEngine()

    breakers = engine.analyze(
        [block]
    )

    assert breakers == []


# =============================================================================
# CONFIRMATION TESTS
# =============================================================================


def test_confirmation_engine_confirms_high_quality_block():

    block = bullish_order_block()

    engine = ConfirmationEngine()

    results = engine.analyze(
        [block]
    )

    assert len(results) == 1

    confirmation = results[0]

    assert confirmation.confirmed is True

    assert confirmation.score >= 50.0

    assert (
        "Order Block Confirmed"
        in block.evidence
    )


def test_confirmation_engine_rejects_invalid_block():

    block = bullish_order_block()

    block.valid = False

    engine = ConfirmationEngine()

    results = engine.analyze(
        [block]
    )

    assert len(results) == 1

    confirmation = results[0]

    assert confirmation.confirmed is False

    assert (
        "Order Block Not Confirmed"
        in block.evidence
    )


# =============================================================================
# MAP TESTS
# =============================================================================


def test_order_block_map_builds_categories():

    bullish = bullish_order_block()

    bearish = bearish_order_block()

    engine = OrderBlockMapEngine()

    result = engine.build(
        blocks=[
            bullish,
            bearish,
        ],
        breakers=[],
    )

    assert len(
        result.all_blocks
    ) == 2

    assert len(
        result.bullish
    ) == 1

    assert len(
        result.bearish
    ) == 1

    assert len(
        result.fresh
    ) == 2


def test_order_block_map_deduplicates_breaker_object():

    block = bullish_order_block()

    block.valid = False

    breaker_engine = BreakerEngine()

    breakers = breaker_engine.analyze(
        [block]
    )

    map_engine = OrderBlockMapEngine()

    result = map_engine.build(
        blocks=[block],
        breakers=breakers,
    )

    assert len(
        result.all_blocks
    ) == 1

    assert len(
        result.breakers
    ) == 1

    assert (
        result.all_blocks[0]
        is block
    )


def test_order_block_map_invalid_block():

    block = bullish_order_block()

    block.valid = False

    block.status = (
        OrderBlockStatus.INVALID
    )

    engine = OrderBlockMapEngine()

    result = engine.build(
        blocks=[block],
        breakers=[],
    )

    assert len(
        result.invalid
    ) == 1


# =============================================================================
# UTILITY FILTER TESTS
# =============================================================================


def test_filter_bullish():

    bullish = bullish_order_block()

    bearish = bearish_order_block()

    result = filter_bullish(
        [
            bullish,
            bearish,
        ]
    )

    assert result == [
        bullish
    ]


def test_filter_bearish():

    bullish = bullish_order_block()

    bearish = bearish_order_block()

    result = filter_bearish(
        [
            bullish,
            bearish,
        ]
    )

    assert result == [
        bearish
    ]


def test_filter_fresh():

    fresh = bullish_order_block()

    tested = bearish_order_block()

    tested.status = (
        OrderBlockStatus.TESTED
    )

    result = filter_fresh(
        [
            fresh,
            tested,
        ]
    )

    assert result == [
        fresh
    ]


def test_filter_mitigated():

    block = bullish_order_block()

    block.status = (
        OrderBlockStatus.MITIGATED
    )

    result = filter_mitigated(
        [block]
    )

    assert result == [
        block
    ]


# =============================================================================
# STATISTICS TESTS
# =============================================================================


def test_average_probability():

    first = bullish_order_block()

    second = bearish_order_block()

    first.probability = 60.0

    second.probability = 80.0

    assert (
        average_probability(
            [
                first,
                second,
            ]
        )
        == 70.0
    )


def test_average_confidence():

    first = bullish_order_block()

    second = bearish_order_block()

    first.confidence = 60.0

    second.confidence = 80.0

    assert (
        average_confidence(
            [
                first,
                second,
            ]
        )
        == 70.0
    )


def test_strongest_order_block():

    weak = bullish_order_block()

    strong = bearish_order_block()

    weak.strength = 40.0

    strong.strength = 90.0

    result = strongest_order_block(
        [
            weak,
            strong,
        ]
    )

    assert result is strong


# =============================================================================
# EMPTY INPUT TESTS
# =============================================================================


def test_engines_handle_empty_input():

    assert (
        BullishOrderBlockEngine().analyze([])
        == []
    )

    assert (
        BearishOrderBlockEngine().analyze([])
        == []
    )

    assert (
        BreakerEngine().analyze([])
        == []
    )

    assert (
        MitigationEngine().analyze([], [])
        == []
    )

    assert (
        ConfirmationEngine().analyze([])
        == []
    )

    assert (
        ProbabilityEngine().calculate([])
        == []
    )

    assert (
        ConfidenceEngine().calculate([])
        == 0.0
    )


# =============================================================================
# PRODUCTION BOUNDARY TESTS
# =============================================================================


@pytest.mark.parametrize(
    "value",
    [
        -100.0,
        0.0,
        50.0,
        100.0,
        200.0,
    ],
)
def test_probability_engine_never_exceeds_bounds(
    value,
):

    block = bullish_order_block()

    block.confidence = value

    block.strength = value

    engine = ProbabilityEngine()

    engine.calculate(
        [block]
    )

    assert 0.0 <= (
        block.probability
    ) <= 100.0


@pytest.mark.parametrize(
    "value",
    [
        -100.0,
        0.0,
        50.0,
        100.0,
        200.0,
    ],
)
def test_confidence_engine_never_exceeds_bounds(
    value,
):

    block = bullish_order_block()

    block.probability = value

    block.strength = value

    engine = ConfidenceEngine()

    confidence = engine.calculate(
        [block]
    )

    assert 0.0 <= confidence <= 100.0

    assert 0.0 <= (
        block.confidence
    ) <= 100.0


# =============================================================================
# MINIMUM DATA CONTRACT
# =============================================================================


def test_minimum_candle_requirement_is_positive():

    assert (
        MIN_CANDLES_REQUIRED >= 3
    )
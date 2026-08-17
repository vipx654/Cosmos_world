"""
===============================================================================
COSMOS Fair Value Gap Tests

Tests for the complete FVG analysis pipeline.

Coverage:

    Validation
        ↓
    Bullish / Bearish Detection
        ↓
    Mitigation
        ↓
    Inversion
        ↓
    Confirmation
        ↓
    Probability
        ↓
    Confidence
        ↓
    FVG Map
        ↓
    Direction
        ↓
    Final FVG Analysis

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest

from ai.agents.fvg.engine import FVGEngine
from ai.agents.fvg.models import (
    FVGAnalysis,
    FVGDirection,
    FVGStatus,
    FVGType,
    FairValueGap,
    MitigationStatus,
    InversionStatus,
)
from ai.agents.fvg.utils import strongest_fvg


# =============================================================================
# TEST CANDLE
# =============================================================================


@dataclass
class TestCandle:
    """
    Minimal candle model compatible with the FVG detectors.

    The real project candle model may contain additional fields.
    These tests intentionally provide the OHLC attributes required
    by the FVG detection layer.
    """

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float


# =============================================================================
# HELPERS
# =============================================================================


def make_candle(
    index: int,
    open_price: float,
    high: float,
    low: float,
    close: float,
) -> TestCandle:

    return TestCandle(
        timestamp=(
            datetime(2026, 1, 5, 9, 0)
            + timedelta(minutes=index)
        ),
        open=open_price,
        high=high,
        low=low,
        close=close,
    )


def make_bullish_fvg_candles() -> list[TestCandle]:
    """
    Construct a three-candle bullish FVG.

    Bullish FVG condition:

        third candle low > first candle high
    """

    return [
        make_candle(
            0,
            100.0,
            101.0,
            99.0,
            100.5,
        ),
        make_candle(
            1,
            100.5,
            105.0,
            100.0,
            104.5,
        ),
        make_candle(
            2,
            104.5,
            106.0,
            103.0,
            105.5,
        ),
    ]


def make_bearish_fvg_candles() -> list[TestCandle]:
    """
    Construct a three-candle bearish FVG.

    Bearish FVG condition:

        third candle high < first candle low
    """

    return [
        make_candle(
            0,
            100.0,
            101.0,
            99.0,
            100.5,
        ),
        make_candle(
            1,
            100.5,
            100.0,
            95.0,
            95.5,
        ),
        make_candle(
            2,
            95.5,
            97.0,
            94.0,
            95.0,
        ),
    ]


def make_neutral_candles() -> list[TestCandle]:
    """
    Construct candles without a meaningful three-candle FVG.
    """

    return [
        make_candle(
            0,
            100.0,
            101.0,
            99.0,
            100.0,
        ),
        make_candle(
            1,
            100.0,
            101.0,
            99.0,
            100.0,
        ),
        make_candle(
            2,
            100.0,
            101.0,
            99.0,
            100.0,
        ),
    ]


# =============================================================================
# MINIMAL CONTEXT
# =============================================================================


class TestContext:
    """
    Minimal MarketContext-compatible object.

    FVGEngine only requires:

        context.candles
    """

    def __init__(self, candles):
        self.candles = candles


# =============================================================================
# MODEL TESTS
# =============================================================================


def test_fvg_direction_enum_values():

    assert FVGDirection.BULLISH.value == "BULLISH"
    assert FVGDirection.BEARISH.value == "BEARISH"
    assert FVGDirection.NEUTRAL.value == "NEUTRAL"


def test_fvg_status_enum_values():

    assert FVGStatus.FRESH.value == "FRESH"
    assert FVGStatus.TESTED.value == "TESTED"
    assert FVGStatus.PARTIAL.value == "PARTIAL"
    assert FVGStatus.FILLED.value == "FILLED"
    assert FVGStatus.INVALID.value == "INVALID"


def test_fvg_model_defaults():

    fvg = FairValueGap(
        fvg_type=FVGType.BULLISH,
        status=FVGStatus.FRESH,
        direction=FVGDirection.BULLISH,
        high=105.0,
        low=101.0,
        first_candle_index=0,
        middle_candle_index=1,
        third_candle_index=2,
        confidence=80.0,
        probability=75.0,
        strength=90.0,
        midpoint=103.0,
    )

    assert fvg.mitigation_status == (
        MitigationStatus.UNTOUCHED
    )

    assert fvg.mitigation_count == 0
    assert fvg.fill_ratio == 0.0
    assert fvg.inverted is False

    assert fvg.inversion_status == (
        InversionStatus.NONE
    )

    assert fvg.valid is True
    assert fvg.timeframe == ""
    assert fvg.source == ""
    assert fvg.evidence == []


# =============================================================================
# UTILITY TESTS
# =============================================================================


def test_strongest_fvg_returns_highest_confidence():

    weak = FairValueGap(
        fvg_type=FVGType.BULLISH,
        status=FVGStatus.FRESH,
        direction=FVGDirection.BULLISH,
        high=105.0,
        low=101.0,
        first_candle_index=0,
        middle_candle_index=1,
        third_candle_index=2,
        confidence=60.0,
        probability=60.0,
        strength=60.0,
        midpoint=103.0,
    )

    strong = FairValueGap(
        fvg_type=FVGType.BULLISH,
        status=FVGStatus.FRESH,
        direction=FVGDirection.BULLISH,
        high=110.0,
        low=106.0,
        first_candle_index=3,
        middle_candle_index=4,
        third_candle_index=5,
        confidence=90.0,
        probability=85.0,
        strength=95.0,
        midpoint=108.0,
    )

    result = strongest_fvg(
        [weak, strong]
    )

    assert result is strong


def test_strongest_fvg_empty_returns_none():

    assert strongest_fvg([]) is None


# =============================================================================
# ENGINE INITIALIZATION
# =============================================================================


def test_fvg_engine_initializes():

    engine = FVGEngine()

    assert engine.validator is not None
    assert engine.bullish_engine is not None
    assert engine.bearish_engine is not None
    assert engine.mitigation_engine is not None
    assert engine.inversion_engine is not None
    assert engine.confirmation_engine is not None
    assert engine.probability_engine is not None
    assert engine.confidence_engine is not None
    assert engine.map_engine is not None


# =============================================================================
# VALIDATION
# =============================================================================


def test_fvg_engine_rejects_none_context():

    engine = FVGEngine()

    with pytest.raises(
        (ValueError, TypeError, AttributeError)
    ):
        engine.analyze(None)


def test_fvg_engine_rejects_empty_context():

    engine = FVGEngine()

    context = TestContext([])

    with pytest.raises(
        (ValueError, TypeError, AttributeError)
    ):
        engine.analyze(context)


# =============================================================================
# BULLISH DETECTION
# =============================================================================


def test_bullish_fvg_engine_detects_gap():

    engine = FVGEngine()

    candles = make_bullish_fvg_candles()

    bullish = engine.bullish_engine.analyze(
        candles
    )

    assert bullish is not None
    assert isinstance(bullish, list)

    assert len(bullish) >= 1

    assert any(
        fvg.direction
        == FVGDirection.BULLISH
        for fvg in bullish
    )


# =============================================================================
# BEARISH DETECTION
# =============================================================================


def test_bearish_fvg_engine_detects_gap():

    engine = FVGEngine()

    candles = make_bearish_fvg_candles()

    bearish = engine.bearish_engine.analyze(
        candles
    )

    assert bearish is not None
    assert isinstance(bearish, list)

    assert len(bearish) >= 1

    assert any(
        fvg.direction
        == FVGDirection.BEARISH
        for fvg in bearish
    )


# =============================================================================
# BULLISH PIPELINE
# =============================================================================


def test_fvg_engine_bullish_pipeline():

    engine = FVGEngine()

    context = TestContext(
        make_bullish_fvg_candles()
    )

    result = engine.analyze(
        context
    )

    assert result is not None
    assert isinstance(
        result,
        FVGAnalysis,
    )

    assert result.fvg_map is not None
    assert isinstance(
        result.fvg_map.all_fvgs,
        list,
    )

    assert len(
        result.fvg_map.all_fvgs
    ) >= 1


# =============================================================================
# BEARISH PIPELINE
# =============================================================================


def test_fvg_engine_bearish_pipeline():

    engine = FVGEngine()

    context = TestContext(
        make_bearish_fvg_candles()
    )

    result = engine.analyze(
        context
    )

    assert result is not None
    assert isinstance(
        result,
        FVGAnalysis,
    )

    assert result.fvg_map is not None

    assert len(
        result.fvg_map.all_fvgs
    ) >= 1


# =============================================================================
# EMPTY / NEUTRAL PIPELINE
# =============================================================================


def test_fvg_engine_handles_no_fvg():

    engine = FVGEngine()

    context = TestContext(
        make_neutral_candles()
    )

    result = engine.analyze(
        context
    )

    assert result is not None
    assert isinstance(
        result,
        FVGAnalysis,
    )

    assert (
        result.direction
        == FVGDirection.NEUTRAL
    )

    assert result.confidence == 0.0
    assert result.probability == 0.0

    assert result.strongest_fvg is None
    assert result.strongest_bullish is None
    assert result.strongest_bearish is None

    assert result.confirmed_fvgs == []

    assert result.reasons


# =============================================================================
# FINAL ANALYSIS CONTRACT
# =============================================================================


def test_fvg_analysis_contract():

    engine = FVGEngine()

    context = TestContext(
        make_bullish_fvg_candles()
    )

    result = engine.analyze(
        context
    )

    assert isinstance(
        result.direction,
        FVGDirection,
    )

    assert isinstance(
        result.confidence,
        float,
    )

    assert isinstance(
        result.probability,
        float,
    )

    assert result.fvg_map is not None

    assert isinstance(
        result.reasons,
        list,
    )

    assert isinstance(
        result.confirmed_fvgs,
        list,
    )


# =============================================================================
# FVG MAP CONTRACT
# =============================================================================


def test_fvg_map_contains_expected_collections():

    engine = FVGEngine()

    context = TestContext(
        make_bullish_fvg_candles()
    )

    result = engine.analyze(
        context
    )

    fvg_map = result.fvg_map

    assert isinstance(
        fvg_map.bullish,
        list,
    )

    assert isinstance(
        fvg_map.bearish,
        list,
    )

    assert isinstance(
        fvg_map.inverted,
        list,
    )

    assert isinstance(
        fvg_map.mitigated,
        list,
    )

    assert isinstance(
        fvg_map.fresh,
        list,
    )

    assert isinstance(
        fvg_map.tested,
        list,
    )

    assert isinstance(
        fvg_map.partial,
        list,
    )

    assert isinstance(
        fvg_map.filled,
        list,
    )

    assert isinstance(
        fvg_map.invalid,
        list,
    )

    assert isinstance(
        fvg_map.all_fvgs,
        list,
    )


# =============================================================================
# RANGE / VALUE SANITY
# =============================================================================


def test_fvg_values_are_sane():

    engine = FVGEngine()

    context = TestContext(
        make_bullish_fvg_candles()
    )

    result = engine.analyze(
        context
    )

    for fvg in result.fvg_map.all_fvgs:

        assert fvg.high >= fvg.low

        assert fvg.high >= 0.0
        assert fvg.low >= 0.0

        assert fvg.midpoint >= fvg.low
        assert fvg.midpoint <= fvg.high

        assert fvg.confidence >= 0.0
        assert fvg.probability >= 0.0
        assert fvg.strength >= 0.0

        assert (
            0.0
            <= fvg.fill_ratio
            <= 1.0
        )


# =============================================================================
# INDEX SANITY
# =============================================================================


def test_fvg_candle_indices_are_ordered():

    engine = FVGEngine()

    context = TestContext(
        make_bullish_fvg_candles()
    )

    result = engine.analyze(
        context
    )

    for fvg in result.fvg_map.all_fvgs:

        assert (
            fvg.first_candle_index
            < fvg.middle_candle_index
        )

        assert (
            fvg.middle_candle_index
            < fvg.third_candle_index
        )


# =============================================================================
# REASONS
# =============================================================================


def test_fvg_analysis_contains_reasons():

    engine = FVGEngine()

    context = TestContext(
        make_bullish_fvg_candles()
    )

    result = engine.analyze(
        context
    )

    assert result.reasons

    for reason in result.reasons:

        assert isinstance(
            reason,
            str,
        )

        assert reason.strip()


# =============================================================================
# DIRECTION CONSISTENCY
# =============================================================================


def test_fvg_direction_matches_confirmed_fvgs():

    engine = FVGEngine()

    bullish_context = TestContext(
        make_bullish_fvg_candles()
    )

    bullish_result = engine.analyze(
        bullish_context
    )

    if (
        bullish_result.direction
        == FVGDirection.BULLISH
    ):

        assert (
            bullish_result.strongest_bullish
            is not None
        )

    elif (
        bullish_result.direction
        == FVGDirection.BEARISH
    ):

        assert (
            bullish_result.strongest_bearish
            is not None
        )

    else:

        assert (
            bullish_result.direction
            == FVGDirection.NEUTRAL
        )


# =============================================================================
# COMPLETE PIPELINE SMOKE TEST
# =============================================================================


def test_fvg_complete_pipeline_smoke():

    engine = FVGEngine()

    bullish_context = TestContext(
        make_bullish_fvg_candles()
    )

    bearish_context = TestContext(
        make_bearish_fvg_candles()
    )

    bullish_result = engine.analyze(
        bullish_context
    )

    bearish_result = engine.analyze(
        bearish_context
    )

    assert isinstance(
        bullish_result,
        FVGAnalysis,
    )

    assert isinstance(
        bearish_result,
        FVGAnalysis,
    )

    assert bullish_result.fvg_map is not None
    assert bearish_result.fvg_map is not None

"""
===============================================================================
COSMOS Liquidity Behavioral Tests

Tests the actual Liquidity Agent detection and scoring behavior.

Coverage:

    • Buy Side Liquidity
    • Sell Side Liquidity
    • Equal-level requirements
    • Liquidity clustering
    • Cluster distance handling
    • Liquidity quality scoring

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.liquidity.buyside_engine import BuySideEngine
from ai.agents.liquidity.sellside_engine import SellSideEngine
from ai.agents.liquidity.cluster_engine import ClusterEngine
from ai.agents.liquidity.quality_engine import QualityEngine

from ai.agents.liquidity.models import (
    LiquidityObject,
    LiquidityType,
    LiquidityStatus,
)


# =============================================================================
# BUY SIDE LIQUIDITY
# =============================================================================


def test_buy_side_detects_equal_highs(
    bullish_swings,
):
    """Buy Side Liquidity should detect equal highs."""

    engine = BuySideEngine()

    result = engine.analyze(
        bullish_swings
    )

    assert result is not None

    for level in result:

        assert (
            level.liquidity_type
            == LiquidityType.BUY_SIDE
        )

        assert (
            level.status
            == LiquidityStatus.UNTOUCHED
        )

        assert level.touches >= 2

        assert 0 <= level.strength <= 100

        assert 0 <= level.confidence <= 100


# =============================================================================
# SELL SIDE LIQUIDITY
# =============================================================================


def test_sell_side_detects_equal_lows(
    bullish_swings,
):
    """Sell Side Liquidity should detect equal lows."""

    engine = SellSideEngine()

    result = engine.analyze(
        bullish_swings
    )

    assert result is not None

    for level in result:

        assert (
            level.liquidity_type
            == LiquidityType.SELL_SIDE
        )

        assert (
            level.status
            == LiquidityStatus.UNTOUCHED
        )

        assert level.touches >= 2

        assert 0 <= level.strength <= 100

        assert 0 <= level.confidence <= 100


# =============================================================================
# EMPTY INPUT
# =============================================================================


def test_buy_side_requires_equal_highs(
    bullish_swings,
):
    """Buy Side Liquidity should return empty for no swings."""

    engine = BuySideEngine()

    result = engine.analyze([])

    assert result == []


def test_sell_side_requires_equal_lows(
    bullish_swings,
):
    """Sell Side Liquidity should return empty for no swings."""

    engine = SellSideEngine()

    result = engine.analyze([])

    assert result == []


# =============================================================================
# CLUSTER ENGINE
# =============================================================================


def test_cluster_engine_groups_nearby_liquidity():
    """Nearby liquidity levels should form a cluster."""

    levels = [

        LiquidityObject(
            liquidity_type=LiquidityType.BUY_SIDE,
            status=LiquidityStatus.UNTOUCHED,
            price=1.10000,
            touches=2,
            strength=60,
            confidence=70,
        ),

        LiquidityObject(
            liquidity_type=LiquidityType.SELL_SIDE,
            status=LiquidityStatus.UNTOUCHED,
            price=1.10005,
            touches=2,
            strength=60,
            confidence=70,
        ),

        LiquidityObject(
            liquidity_type=LiquidityType.INTERNAL,
            status=LiquidityStatus.UNTOUCHED,
            price=1.10010,
            touches=1,
            strength=50,
            confidence=55,
        ),

    ]

    engine = ClusterEngine()

    clusters = engine.analyze(
        levels
    )

    assert clusters

    assert len(
        clusters[0]
    ) >= 3


# =============================================================================
# DISTANT LIQUIDITY
# =============================================================================


def test_cluster_engine_rejects_distant_levels():
    """Distant liquidity levels should not form a cluster."""

    levels = [

        LiquidityObject(
            liquidity_type=LiquidityType.BUY_SIDE,
            status=LiquidityStatus.UNTOUCHED,
            price=1.10000,
            touches=2,
            strength=60,
            confidence=70,
        ),

        LiquidityObject(
            liquidity_type=LiquidityType.SELL_SIDE,
            status=LiquidityStatus.UNTOUCHED,
            price=1.20000,
            touches=2,
            strength=60,
            confidence=70,
        ),

        LiquidityObject(
            liquidity_type=LiquidityType.INTERNAL,
            status=LiquidityStatus.UNTOUCHED,
            price=1.30000,
            touches=1,
            strength=50,
            confidence=55,
        ),

    ]

    engine = ClusterEngine()

    clusters = engine.analyze(
        levels
    )

    assert clusters == []


# =============================================================================
# QUALITY ENGINE
# =============================================================================


def test_quality_engine_calculates_quality():
    """Quality Engine should calculate a bounded quality score."""

    levels = [

        LiquidityObject(
            liquidity_type=LiquidityType.BUY_SIDE,
            status=LiquidityStatus.UNTOUCHED,
            price=1.10000,
            touches=3,
            strength=80,
            confidence=90,
        )

    ]

    engine = QualityEngine()

    result = engine.analyze(
        levels
    )

    assert result is levels

    assert (
        result[0].quality > 0
    )

    assert (
        result[0].quality <= 100
    )
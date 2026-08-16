"""
===============================================================================
COSMOS Liquidity Agent Tests

Tests the Liquidity Agent independently.

Pipeline dependency:

    Trend
        ↓
    Market Structure
        ↓
    SMC
        ↓
    Liquidity

===============================================================================
"""

from __future__ import annotations

from ai.agents.trend.engine import TrendEngine
from ai.agents.market_structure.engine import MarketStructureEngine
from ai.agents.smc.engine import SMCEngine
from ai.agents.liquidity.engine import LiquidityEngine


def test_liquidity_engine_analyzes_market(
    market_context,
    bullish_swings,
):
    """
    Run Trend → Market Structure → SMC → Liquidity.
    """

    # =========================================================================
    # 1. TREND
    # =========================================================================

    trend_engine = TrendEngine()

    trend_result = trend_engine.analyze(
        market_context
    )

    assert trend_result is not None
    assert trend_result.success is True
    assert trend_result.name == "trend"

    # =========================================================================
    # 2. TREND SHARED MEMORY
    # =========================================================================

    market_context.memory["trend"] = {
        "swings": bullish_swings,
        "analysis": trend_result.analysis,
        "result": trend_result,
    }

    assert "trend" in market_context.memory

    # =========================================================================
    # 3. MARKET STRUCTURE
    # =========================================================================

    market_structure_engine = MarketStructureEngine()

    market_structure_result = (
        market_structure_engine.analyze(
            market_context
        )
    )

    assert market_structure_result is not None
    assert market_structure_result.success is True
    assert (
        market_structure_result.name
        == "market_structure"
    )

    assert "market_structure" in market_context.memory

    # =========================================================================
    # 4. SMC
    # =========================================================================

    smc_engine = SMCEngine()

    smc_result = smc_engine.analyze(
        market_context
    )

    assert smc_result is not None
    assert smc_result.success is True
    assert smc_result.name == "smc"

    assert "smc" in market_context.memory

    # =========================================================================
    # 5. LIQUIDITY
    # =========================================================================

    liquidity_engine = LiquidityEngine()

    liquidity_result = liquidity_engine.analyze(
        market_context
    )

    assert liquidity_result is not None
    assert liquidity_result.success is True
    assert liquidity_result.name == "liquidity"

    # =========================================================================
    # 6. LIQUIDITY SHARED MEMORY
    # =========================================================================

    assert "liquidity" in market_context.memory

    liquidity_memory = (
        market_context.memory["liquidity"]
    )

    assert liquidity_memory is not None

    assert "buy_side" in liquidity_memory
    assert "sell_side" in liquidity_memory
    assert "internal" in liquidity_memory
    assert "external" in liquidity_memory
    assert "clusters" in liquidity_memory
    assert "map" in liquidity_memory
    assert "confidence" in liquidity_memory

    # =========================================================================
    # 7. LIQUIDITY ANALYSIS
    # =========================================================================

    analysis = liquidity_result.analysis

    assert analysis is not None
    assert analysis.liquidity_map is not None

    assert 0 <= analysis.confidence <= 100

    # =========================================================================
    # 8. LIQUIDITY MAP
    # =========================================================================

    liquidity_map = analysis.liquidity_map

    assert liquidity_map is not None
    assert liquidity_map.buy_side is not None
    assert liquidity_map.sell_side is not None
    assert liquidity_map.internal is not None
    assert liquidity_map.external is not None
    assert liquidity_map.clusters is not None
    assert liquidity_map.all_levels is not None

    # =========================================================================
    # 9. RESULT REGISTRY
    # =========================================================================

    assert "trend" in market_context.results
    assert "market_structure" in market_context.results
    assert "smc" in market_context.results
    assert "liquidity" in market_context.results


def test_liquidity_engine_metadata():

    engine = LiquidityEngine()

    assert engine.AGENT_NAME == "liquidity"
    assert engine.AGENT_VERSION == "1.0.0"
    assert engine.AGENT_AUTHOR == "COSMOS"


def test_liquidity_engine_subsystems():

    engine = LiquidityEngine()

    assert engine.buy_side_engine is not None
    assert engine.sell_side_engine is not None
    assert engine.internal_engine is not None
    assert engine.external_engine is not None
    assert engine.cluster_engine is not None
    assert engine.quality_engine is not None
    assert engine.map_engine is not None
    assert engine.confidence_engine is not None
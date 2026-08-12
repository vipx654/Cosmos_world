"""
===============================================================================
COSMOS Sweep Integration Test

Tests the complete upstream dependency pipeline required by the Sweep system.

Pipeline:

    Trend
        ↓
    Market Structure
        ↓
    SMC
        ↓
    Liquidity
        ↓
    Sweep

The test uses the deterministic `bullish_swings` fixture for downstream
structural analysis so the integration test does not depend on the generic
market candle fixture accidentally producing the required swing sequence.
===============================================================================
"""

from __future__ import annotations


from ai.agents.trend.engine import (
    TrendEngine,
)

from ai.agents.trend.swing_engine import (
    SwingEngine,
)

from ai.agents.market_structure.engine import (
    MarketStructureEngine,
)

from ai.agents.smc.engine import (
    SMCEngine,
)

from ai.agents.liquidity.engine import (
    LiquidityEngine,
)

from ai.agents.sweep.engine import (
    SweepEngine,
)


def test_sweep_engine_analyzes_market(
    market_context,
    bullish_swings,
):
    """
    Run the complete Trend → Market Structure → SMC → Liquidity → Sweep
    integration pipeline.
    """

    # =========================================================================
    # 1. TREND
    # =========================================================================

    trend_engine = (
        TrendEngine()
    )

    trend_result = (
        trend_engine.analyze(
            market_context
        )
    )

    assert trend_result is not None

    assert (
        trend_result.success
        is True
    )

    assert (
        trend_result.name
        == "trend"
    )

    # =========================================================================
    # 2. DETERMINISTIC SWING DATA
    # =========================================================================
    #
    # The generic candle fixture is used by the real Trend Engine above.
    #
    # For downstream structural agents we use the dedicated bullish_swings
    # fixture so BOS / CHOCH / Market Structure / Liquidity / Sweep analysis
    # receives deterministic swing data.
    # =========================================================================

    assert (
        bullish_swings
        is not None
    )

    assert (
        len(bullish_swings)
        > 0
    )

    # =========================================================================
    # 3. BUILD TREND SHARED MEMORY
    # =========================================================================

    market_context.memory[
        "trend"
    ] = {

        "swings": (
            bullish_swings
        ),

        "analysis": (
            trend_result.analysis
        ),

        "result": (
            trend_result
        ),
    }

    assert (
        "trend"
        in market_context.memory
    )

    assert (
        market_context.memory[
            "trend"
        ][
            "swings"
        ]
        == bullish_swings
    )

    # =========================================================================
    # 4. MARKET STRUCTURE
    # =========================================================================

    market_structure_engine = (
        MarketStructureEngine()
    )

    market_structure_result = (
        market_structure_engine.analyze(
            market_context
        )
    )

    assert (
        market_structure_result
        is not None
    )

    assert (
        market_structure_result.success
        is True
    )

    assert (
        market_structure_result.name
        == "market_structure"
    )

    # =========================================================================
    # 5. MARKET STRUCTURE SHARED MEMORY
    # =========================================================================

    assert (
        "market_structure"
        in market_context.memory
    )

    assert (
        market_context.memory[
            "market_structure"
        ]
        is not None
    )

    # =========================================================================
    # 6. SMC
    # =========================================================================

    smc_engine = (
        SMCEngine()
    )

    smc_result = (
        smc_engine.analyze(
            market_context
        )
    )

    assert (
        smc_result
        is not None
    )

    assert (
        smc_result.success
        is True
    )

    assert (
        smc_result.name
        == "smc"
    )

    # =========================================================================
    # 7. SMC SHARED MEMORY
    # =========================================================================

    assert (
        "smc"
        in market_context.memory
    )

    assert (
        market_context.memory[
            "smc"
        ]
        is not None
    )

    # =========================================================================
    # 8. LIQUIDITY
    # =========================================================================

    liquidity_engine = (
        LiquidityEngine()
    )

    liquidity_result = (
        liquidity_engine.analyze(
            market_context
        )
    )

    assert (
        liquidity_result
        is not None
    )

    assert (
        liquidity_result.success
        is True
    )

    assert (
        liquidity_result.name
        == "liquidity"
    )

    # =========================================================================
    # 9. LIQUIDITY SHARED MEMORY
    # =========================================================================

    assert (
        "liquidity"
        in market_context.memory
    )

    assert (
        market_context.memory[
            "liquidity"
        ]
        is not None
    )

    # =========================================================================
    # 10. SWEEP
    # =========================================================================

    sweep_engine = (
        SweepEngine()
    )

    sweep_result = (
        sweep_engine.analyze(
            market_context
        )
    )

    assert (
        sweep_result
        is not None
    )

    assert (
        sweep_result.success
        is True
    )

    assert (
        sweep_result.name
        == "sweep"
    )

    # =========================================================================
    # 11. SWEEP SHARED MEMORY
    # =========================================================================

    assert (
        "sweep"
        in market_context.memory
    )

    assert (
        market_context.memory[
            "sweep"
        ]
        is not None
    )

    # =========================================================================
    # 12. RESULT REGISTRY
    # =========================================================================

    assert (
        "trend"
        in market_context.results
    )

    assert (
        "market_structure"
        in market_context.results
    )

    assert (
        "smc"
        in market_context.results
    )

    assert (
        "liquidity"
        in market_context.results
    )

    assert (
        "sweep"
        in market_context.results
    )
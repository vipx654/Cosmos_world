"""
===============================================================================
COSMOS SMC Agent Tests

Behavioral tests for the Smart Money Concept Agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from ai.agents.smc.engine import SMCEngine
from ai.agents.trend.swing_engine import SwingEngine
from ai.agents.smc.models import SMCAnalysis
from ai.models import AgentResult


def test_smc_engine_analyzes_market(
    market_context,
):
    swing_engine = SwingEngine()

    swings = swing_engine.detect(
        market_context.candles
    )

    market_context.memory = {
        "trend": {
            "swings": swings,
        }
    }

    engine = SMCEngine()

    result = engine.analyze(
        market_context
    )

    assert result is not None

    assert isinstance(
        result,
        AgentResult,
    )

    assert result.name == "smc"

    assert result.success is True

    assert 0.0 <= result.confidence <= 100.0

    assert isinstance(
        result.analysis,
        SMCAnalysis,
    )

    assert "smc" in market_context.results

    assert market_context.results["smc"] is result

    assert "smc" in market_context.memory

    smc_memory = market_context.memory["smc"]

    assert "dealing_range" in smc_memory

    assert "premium_discount" in smc_memory

    assert "fvg" in smc_memory

    assert "equal_high" in smc_memory

    assert "equal_low" in smc_memory

    assert "inducement" in smc_memory

    assert "confidence" in smc_memory
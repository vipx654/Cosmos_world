"""
===============================================================================
COSMOS Trend Agent Tests

Behavioral tests for the Trend Agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from ai.agents.trend.engine import TrendEngine
from ai.models import TrendAnalysis
from ai.models import TrendDirection


def test_trend_engine_analyzes_market(
    market_context,
):
    engine = TrendEngine()

    result = engine.analyze(
        market_context
    )

    assert result is not None

    assert result.name == "trend"

    assert result.success is True

    assert 0.0 <= result.confidence <= 100.0

    assert isinstance(
        result.analysis,
        TrendAnalysis,
    )

    analysis = result.analysis

    assert analysis.direction in (
        TrendDirection.BULLISH,
        TrendDirection.BEARISH,
        TrendDirection.SIDEWAYS,
        TrendDirection.UNKNOWN,
    )

    assert 0.0 <= analysis.confidence <= 100.0

    assert 0.0 <= analysis.strength <= 100.0

    assert isinstance(
        analysis.structure,
        str,
    )

    assert isinstance(
        analysis.structures,
        list,
    )

    assert isinstance(
        analysis.acceleration,
        bool,
    )

    assert isinstance(
        analysis.momentum,
        (int, float),
    )

    assert isinstance(
        analysis.reasons,
        list,
    )
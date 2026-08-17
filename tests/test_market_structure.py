"""
===============================================================================
COSMOS Market Structure Tests

Tests for the institutional Market Structure Agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from ai.agents.market_structure.models import (
    StructureBias,
    StructureLevel,
    StructureLevelType,
)

from ai.agents.market_structure.structure_engine import (
    StructureEngine,
)


# =============================================================================
# TEST SWING MODEL
# =============================================================================


@dataclass(slots=True)
class TestSwing:
    """
    Lightweight swing object used by the structure tests.
    """

    price: float
    index: int
    swing_type: object


# =============================================================================
# HELPERS
# =============================================================================


def high(
    price: float,
    index: int,
) -> TestSwing:

    from ai.models import SwingType

    return TestSwing(
        price=price,
        index=index,
        swing_type=SwingType.HIGH,
    )


def low(
    price: float,
    index: int,
) -> TestSwing:

    from ai.models import SwingType

    return TestSwing(
        price=price,
        index=index,
        swing_type=SwingType.LOW,
    )


# =============================================================================
# BASIC STRUCTURE TESTS
# =============================================================================


def test_structure_engine_empty_swings():

    engine = StructureEngine()

    result = engine.analyze([])

    assert result.higher_highs == 0
    assert result.higher_lows == 0
    assert result.lower_highs == 0
    assert result.lower_lows == 0

    assert result.bias == StructureBias.NEUTRAL


def test_structure_engine_bullish_structure():

    engine = StructureEngine()

    swings = [
        high(100.0, 1),
        low(90.0, 2),
        high(110.0, 3),
        low(95.0, 4),
        high(120.0, 5),
        low(105.0, 6),
    ]

    result = engine.analyze(swings)

    assert result.higher_highs == 2
    assert result.higher_lows == 2

    assert result.lower_highs == 0
    assert result.lower_lows == 0

    assert result.bias == StructureBias.BULLISH


def test_structure_engine_bearish_structure():

    engine = StructureEngine()

    swings = [
        high(120.0, 1),
        low(100.0, 2),
        high(110.0, 3),
        low(90.0, 4),
        high(100.0, 5),
        low(80.0, 6),
    ]

    result = engine.analyze(swings)

    assert result.lower_highs == 2
    assert result.lower_lows == 2

    assert result.higher_highs == 0
    assert result.higher_lows == 0

    assert result.bias == StructureBias.BEARISH


def test_structure_engine_neutral_structure():

    engine = StructureEngine()

    swings = [
        high(100.0, 1),
        low(90.0, 2),
        high(110.0, 3),
        low(85.0, 4),
        high(105.0, 5),
        low(95.0, 6),
    ]

    result = engine.analyze(swings)

    assert result.bias == StructureBias.NEUTRAL


# =============================================================================
# PROTECTED LEVEL TESTS
# =============================================================================


def test_structure_engine_returns_protected_high():

    engine = StructureEngine()

    swings = [
        high(100.0, 1),
        low(90.0, 2),
        high(110.0, 3),
        low(95.0, 4),
        high(120.0, 5),
        low(105.0, 6),
    ]

    result = engine.analyze(swings)

    assert result.protected_high is not None

    assert isinstance(
        result.protected_high,
        StructureLevel,
    )

    assert (
        result.protected_high.level_type
        == StructureLevelType.HIGH
    )

    assert result.protected_high.price == 120.0


def test_structure_engine_returns_protected_low():

    engine = StructureEngine()

    swings = [
        high(100.0, 1),
        low(90.0, 2),
        high(110.0, 3),
        low(95.0, 4),
        high(120.0, 5),
        low(105.0, 6),
    ]

    result = engine.analyze(swings)

    assert result.protected_low is not None

    assert isinstance(
        result.protected_low,
        StructureLevel,
    )

    assert (
        result.protected_low.level_type
        == StructureLevelType.LOW
    )

    assert result.protected_low.price == 105.0


# =============================================================================
# STRUCTURE STRENGTH
# =============================================================================


def test_structure_strength_is_bounded():

    engine = StructureEngine()

    swings = [
        high(100.0, 1),
        low(90.0, 2),
        high(110.0, 3),
        low(95.0, 4),
        high(120.0, 5),
        low(105.0, 6),
        high(130.0, 7),
        low(115.0, 8),
    ]

    result = engine.analyze(swings)

    assert 0.0 <= result.strength <= 100.0
    assert 0.0 <= result.confidence <= 100.0


# =============================================================================
# DATA INTEGRITY
# =============================================================================


def test_structure_engine_does_not_modify_swings():

    engine = StructureEngine()

    swings = [
        high(100.0, 1),
        low(90.0, 2),
        high(110.0, 3),
        low(95.0, 4),
    ]

    original = [
        (
            swing.price,
            swing.index,
            swing.swing_type,
        )
        for swing in swings
    ]

    engine.analyze(swings)

    current = [
        (
            swing.price,
            swing.index,
            swing.swing_type,
        )
        for swing in swings
    ]

    assert current == original


# =============================================================================
# INVALID INPUT
# =============================================================================


def test_structure_engine_requires_swing_objects():

    engine = StructureEngine()

    with pytest.raises(
        (AttributeError, TypeError),
    ):
        engine.analyze(
            [None]
        )
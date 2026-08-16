"""
===============================================================================
COSMOS Test Fixtures

Shared market-data fixtures used by the COSMOS behavioral test suite.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from ai.context import MarketContext
from ai.models import MarketCandle
from ai.models import SwingPoint
from ai.models import SwingType


@pytest.fixture
def market_candles() -> list[MarketCandle]:
    """
    Provide a deterministic OHLCV dataset for agent testing.
    """

    start = datetime(
        2026,
        1,
        5,
        9,
        0,
        0,
    )

    data = [

    (100.0, 101.0, 99.0, 100.5, 1000.0),
    (100.5, 102.0, 100.0, 101.5, 1100.0),
    (101.5, 103.0, 101.0, 102.5, 1200.0),
    (102.5, 102.8, 100.8, 101.2, 900.0),
    (101.2, 104.0, 101.0, 103.5, 1500.0),
    (103.5, 105.0, 103.0, 104.5, 1700.0),
    (104.5, 105.0, 102.5, 103.0, 1300.0),
    (103.0, 106.0, 102.8, 105.5, 1900.0),
    (105.5, 107.0, 105.0, 106.5, 2100.0),
    (106.5, 107.0, 104.5, 105.0, 1400.0),
    (105.0, 108.0, 104.8, 107.5, 2300.0),
    (107.5, 109.0, 107.0, 108.5, 2500.0),
    (108.5, 109.0, 106.5, 107.0, 1600.0),
    (107.0, 110.0, 106.8, 109.5, 2700.0),
    (109.5, 111.0, 109.0, 110.5, 2900.0),
    (110.5, 111.0, 108.5, 109.0, 1800.0),
    (109.0, 112.0, 108.8, 111.5, 3100.0),
    (111.5, 113.0, 111.0, 112.5, 3300.0),
    (112.5, 113.0, 110.5, 111.0, 2000.0),
    (111.0, 114.0, 110.8, 113.5, 3500.0),
    ]

    return [

        MarketCandle(
            timestamp=(
                start + timedelta(minutes=index)
            ),
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume,
        )

        for index, (
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
        ) in enumerate(data)
    ]


@pytest.fixture
def market_context(
    market_candles: list[MarketCandle],
) -> MarketContext:
    """
    Provide a deterministic shared MarketContext.
    """

    return MarketContext(

        symbol="EURUSD",

        timeframe="M5",

        candles=market_candles,

        broker="TEST",

        spread=0.0001,

        account_balance=5000.0,

        leverage=100,
    )


@pytest.fixture
def bullish_swings() -> list[SwingPoint]:
    """
    Provide a bullish swing sequence for structure testing.
    """

    base = datetime(
        2026,
        1,
        5,
        9,
        0,
        0,
    )

    return [

        SwingPoint(
            index=2,
            price=101.0,
            timestamp=base + timedelta(minutes=2),
            swing_type=SwingType.LOW,
        ),

        SwingPoint(
            index=4,
            price=104.0,
            timestamp=base + timedelta(minutes=4),
            swing_type=SwingType.HIGH,
        ),

        SwingPoint(
            index=6,
            price=103.0,
            timestamp=base + timedelta(minutes=6),
            swing_type=SwingType.LOW,
        ),

        SwingPoint(
            index=8,
            price=107.0,
            timestamp=base + timedelta(minutes=8),
            swing_type=SwingType.HIGH,
        ),

        SwingPoint(
            index=10,
            price=105.0,
            timestamp=base + timedelta(minutes=10),
            swing_type=SwingType.LOW,
        ),

        SwingPoint(
            index=12,
            price=110.0,
            timestamp=base + timedelta(minutes=12),
            swing_type=SwingType.HIGH,
        ),

        SwingPoint(
            index=14,
            price=108.0,
            timestamp=base + timedelta(minutes=14),
            swing_type=SwingType.LOW,
        ),

        SwingPoint(
            index=16,
            price=113.0,
            timestamp=base + timedelta(minutes=16),
            swing_type=SwingType.HIGH,
        ),
    ]
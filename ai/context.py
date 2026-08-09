"""
===============================================================================
COSMOS AI Context

Shared market context passed between every AI agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai.models import AgentResult
from ai.models import MarketCandle


@dataclass(slots=True)
class MarketContext:
    """
    Shared context exchanged between every AI agent.
    """

    # -------------------------------------------------------------------------
    # Raw Market Data
    # -------------------------------------------------------------------------

    symbol: str

    timeframe: str

    candles: list[MarketCandle]

    # -------------------------------------------------------------------------
    # Analysis Cache
    # -------------------------------------------------------------------------

    results: dict[str, AgentResult] = field(default_factory=dict)

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    broker: str | None = None

    spread: float = 0.0

    account_balance: float = 0.0

    leverage: int = 1

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------

    def add_result(
        self,
        result: AgentResult,
    ) -> None:
        """
        Store an agent result.
        """

        self.results[result.name] = result

    def get_result(
        self,
        name: str,
    ) -> AgentResult | None:
        """
        Retrieve an agent result.
        """

        return self.results.get(name)
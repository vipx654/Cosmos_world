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
from ai.models import ChartAnnotation
from ai.models import MarketCandle


@dataclass(slots=True)
class MarketContext:
    """
    Shared context exchanged between every AI agent.

    The context contains:

        - raw market data
        - agent results
        - shared agent memory
        - chart annotations

    Chart annotations provide the bridge between AI analysis
    and the future COSMOS chart/UI layer.
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

    results: dict[str, AgentResult] = field(
        default_factory=dict
    )

    # -------------------------------------------------------------------------
    # Shared Agent Memory
    # -------------------------------------------------------------------------

    memory: dict[str, dict] = field(
        default_factory=dict
    )

    # -------------------------------------------------------------------------
    # Chart Annotations
    # -------------------------------------------------------------------------
    #
    # Every intelligent agent can publish visual analysis here.
    #
    # Example:
    #
    #     Trend Agent
    #         ↓
    #     Bullish Trendline
    #         ↓
    #     ChartAnnotation
    #         ↓
    #     context.annotations
    #         ↓
    #     COSMOS Chart
    #
    # Locked annotations represent analysis that the agent has
    # finalized and wants the chart to preserve.
    # -------------------------------------------------------------------------

    annotations: list[ChartAnnotation] = field(
        default_factory=list
    )

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    broker: str | None = None

    spread: float = 0.0

    account_balance: float = 0.0

    leverage: int = 1

    # =========================================================================
    # RESULT UTILITY
    # =========================================================================

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

    # =========================================================================
    # ANNOTATION UTILITY
    # =========================================================================

    def add_annotation(
        self,
        annotation: ChartAnnotation,
    ) -> None:
        """
        Add a chart annotation.

        Duplicate annotation IDs are replaced instead of
        creating multiple copies of the same visual object.
        """

        for index, existing in enumerate(
            self.annotations
        ):

            if existing.id == annotation.id:

                self.annotations[index] = annotation

                return

        self.annotations.append(
            annotation
        )

    def add_annotations(
        self,
        annotations: list[ChartAnnotation],
    ) -> None:
        """
        Add multiple chart annotations.
        """

        for annotation in annotations:

            self.add_annotation(
                annotation
            )

    def get_annotations(
        self,
    ) -> list[ChartAnnotation]:
        """
        Return all chart annotations.
        """

        return list(
            self.annotations
        )

    def get_agent_annotations(
        self,
        agent: str,
    ) -> list[ChartAnnotation]:
        """
        Return annotations produced by one agent.
        """

        return [
            annotation
            for annotation in self.annotations
            if annotation.agent == agent
        ]

    def get_locked_annotations(
        self,
    ) -> list[ChartAnnotation]:
        """
        Return only locked annotations.

        Locked annotations represent finalized analysis
        that should remain available to the chart layer.
        """

        return [
            annotation
            for annotation in self.annotations
            if annotation.locked
        ]

    def clear_annotations(
        self,
    ) -> None:
        """
        Remove all chart annotations.

        This is intended for starting a fresh analysis cycle.
        """

        self.annotations.clear()
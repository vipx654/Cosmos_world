"""
===============================================================================
COSMOS Brain

Central AI Brain.

Coordinates all agents and returns one unified decision.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.decision_engine import decision_engine
from ai.orchestrator import orchestrator


class CosmosBrain:
    """
    Main AI Brain.

    Entry point for every market analysis.
    """

    def analyze(
        self,
        market_data: dict,
    ) -> dict:

        orchestrator.run(market_data)

        return decision_engine.evaluate()

    # ------------------------------------------------------------------

    def register_agent(
        self,
        agent,
    ) -> None:

        orchestrator.register(agent)

    # ------------------------------------------------------------------

    def registered_agents(self):

        return orchestrator.registered_agents()

    # ------------------------------------------------------------------

    def reset(self):

        orchestrator.clear()


brain = CosmosBrain()
"""
===============================================================================
COSMOS AI Orchestrator

Runs every AI agent in sequence and stores their outputs.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.base_agent import BaseAgent
from ai.memory import memory


class AIOrchestrator:
    """
    Coordinates all AI agents.
    """

    def __init__(self):

        self.agents: list[BaseAgent] = []

    # ------------------------------------------------------------------

    def register(
        self,
        agent: BaseAgent,
    ) -> None:

        self.agents.append(agent)

    # ------------------------------------------------------------------

    def unregister(
        self,
        agent_name: str,
    ) -> None:

        self.agents = [
            agent
            for agent in self.agents
            if agent.name != agent_name
        ]

    # ------------------------------------------------------------------

    def clear(self):

        self.agents.clear()

    # ------------------------------------------------------------------

    def run(
        self,
        market_data: dict,
    ):

        memory.clear()

        for agent in self.agents:

            agent.reset()

            agent.analyze(market_data)

        return memory.all()

    # ------------------------------------------------------------------

    def registered_agents(self):

        return [
            agent.name
            for agent in self.agents
        ]


orchestrator = AIOrchestrator()
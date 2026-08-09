"""
===============================================================================
COSMOS AI Memory

Shared memory for all AI agents.

Every agent writes its analysis here.
The Decision Engine reads this memory to build the final trade decision.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AgentMemory:

    name: str

    confidence: float = 0.0

    signal: str = "NEUTRAL"

    data: dict[str, Any] = field(default_factory=dict)

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class CosmosMemory:
    """
    Central shared memory.

    Every AI agent stores its latest result here.
    """

    def __init__(self):

        self._memory: dict[str, AgentMemory] = {}

    # ------------------------------------------------------------------

    def update(
        self,
        agent: str,
        signal: str,
        confidence: float,
        **data,
    ) -> None:

        self._memory[agent] = AgentMemory(
            name=agent,
            signal=signal,
            confidence=confidence,
            data=data,
        )

    # ------------------------------------------------------------------

    def get(
        self,
        agent: str,
    ) -> AgentMemory | None:

        return self._memory.get(agent)

    # ------------------------------------------------------------------

    def all(self) -> list[AgentMemory]:

        return list(self._memory.values())

    # ------------------------------------------------------------------

    def clear(self):

        self._memory.clear()

    # ------------------------------------------------------------------

    def summary(self) -> dict:

        return {
            item.name: {
                "signal": item.signal,
                "confidence": item.confidence,
            }
            for item in self._memory.values()
        }


memory = CosmosMemory()
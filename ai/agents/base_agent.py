"""
===============================================================================
COSMOS Base Agent

Base class inherited by every COSMOS AI Agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from ai.memory import memory


class BaseAgent(ABC):
    """
    Base AI Agent.

    Every intelligent agent inherits this class.
    """

    name: str = "BaseAgent"

    def __init__(self):

        self.signal = "NEUTRAL"

        self.confidence = 0.0

        self.data: dict = {}

    # ------------------------------------------------------------------

    @abstractmethod
    def analyze(
        self,
        market_data: dict,
    ) -> None:
        """
        Perform market analysis.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------

    def commit(self):

        memory.update(
            agent=self.name,
            signal=self.signal,
            confidence=self.confidence,
            **self.data,
        )

    # ------------------------------------------------------------------

    def reset(self):

        self.signal = "NEUTRAL"

        self.confidence = 0.0

        self.data.clear()
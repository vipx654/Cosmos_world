"""
===============================================================================
COSMOS Market Structure Models

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StructureBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


@dataclass(slots=True)
class MarketStructureAnalysis:
    """
    Final output of the Market Structure Agent.
    """

    bullish_bos: bool

    bearish_bos: bool

    choch: bool

    mss: bool

    internal_bias: StructureBias

    external_bias: StructureBias

    confidence: float

    reasons: list[str]
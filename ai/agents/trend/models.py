"""
===============================================================================
COSMOS Trend Agent Models

Internal models used by the Trend Agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ai.models import SwingPoint


class StructureType(str, Enum):
    HH = "HIGHER_HIGH"
    HL = "HIGHER_LOW"
    LH = "LOWER_HIGH"
    LL = "LOWER_LOW"


@dataclass(slots=True)
class TrendStructure:
    """
    Represents the current market structure.
    """

    highs: list[SwingPoint]

    lows: list[SwingPoint]

    structure: list[StructureType]


@dataclass(slots=True)
class TrendScore:
    """
    Internal confidence scoring.
    """

    structure_score: float = 0.0

    momentum_score: float = 0.0

    ema_score: float = 0.0

    trendline_score: float = 0.0

    total_score: float = 0.0
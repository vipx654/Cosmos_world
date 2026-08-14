"""
===============================================================================
COSMOS Sweep Models

Production data contracts for institutional liquidity sweep analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SweepType(str, Enum):
    """Classification of the liquidity level that was swept."""

    BUY_SIDE = "BUY_SIDE"
    SELL_SIDE = "SELL_SIDE"
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    UNKNOWN = "UNKNOWN"


class SweepStatus(str, Enum):
    """Lifecycle state of a detected sweep."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    INVALID = "INVALID"


class SweepDirection(str, Enum):
    """Expected directional implication of a sweep."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class SweepQuality(str, Enum):
    """Quality classification derived from sweep evidence."""

    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    EXCEPTIONAL = "EXCEPTIONAL"


@dataclass(slots=True)
class SweepObject:
    """
    Represents one detected liquidity sweep.

    The object is intentionally mutable because later pipeline stages
    progressively enrich the same sweep with probability, confidence,
    confirmation, session and evidence information.
    """

    sweep_type: SweepType
    status: SweepStatus
    direction: SweepDirection

    price: float
    candle_index: int

    confidence: float = 0.0
    probability: float = 0.0
    strength: float = 0.0

    fake: bool = False

    session: str = ""
    source: str = ""

    # Price-action measurements.
    penetration: float = 0.0
    rejection: float = 0.0
    candle_range: float = 0.0
    body_size: float = 0.0

    # Optional candle timestamp. Kept generic so existing MarketCandle
    # implementations do not need to be changed.
    timestamp: object | None = None

    quality: SweepQuality = SweepQuality.WEAK

    evidence: list[str] = field(default_factory=list)

    def add_evidence(self, message: str) -> None:
        """Add unique evidence without creating duplicate entries."""

        if message and message not in self.evidence:
            self.evidence.append(message)

    def clamp_scores(self) -> None:
        """Keep model scores inside their valid 0-100 range."""

        self.confidence = max(
            0.0,
            min(100.0, float(self.confidence)),
        )

        self.probability = max(
            0.0,
            min(100.0, float(self.probability)),
        )

        self.strength = max(
            0.0,
            min(100.0, float(self.strength)),
        )

    def update_quality(self) -> SweepQuality:
        """Derive a deterministic quality classification."""

        score = (
            self.confidence
            + self.probability
            + self.strength
        ) / 3.0

        if score >= 90.0:
            self.quality = SweepQuality.EXCEPTIONAL
        elif score >= 75.0:
            self.quality = SweepQuality.STRONG
        elif score >= 60.0:
            self.quality = SweepQuality.MODERATE
        else:
            self.quality = SweepQuality.WEAK

        return self.quality


@dataclass(slots=True)
class SweepMap:
    """
    Aggregated sweep information produced by the Sweep Agent.
    """

    buy_side: list[SweepObject] = field(default_factory=list)
    sell_side: list[SweepObject] = field(default_factory=list)

    fake_sweeps: list[SweepObject] = field(default_factory=list)
    confirmed: list[SweepObject] = field(default_factory=list)

    all_sweeps: list[SweepObject] = field(default_factory=list)


@dataclass(slots=True)
class SweepAnalysis:
    """
    Final output of the Sweep Agent.
    """

    direction: SweepDirection

    confidence: float
    probability: float

    sweep_map: SweepMap

    reasons: list[str] = field(default_factory=list)
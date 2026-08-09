"""
===============================================================================
COSMOS Volume Agent Models

Shared data models for volume analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# =============================================================================
# ENUMS
# =============================================================================


class VolumeType(str, Enum):
    """
    Type of volume data available to COSMOS.
    """

    TICK = "tick"
    REAL = "real"
    UNKNOWN = "unknown"


class VolumeState(str, Enum):
    """
    General volume activity state.
    """

    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    EXTREME = "extreme"


class VolumeDirection(str, Enum):
    """
    Direction associated with price/volume behavior.
    """

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class VolumeSignalType(str, Enum):
    """
    Main volume signal categories.
    """

    SPIKE = "spike"
    TREND = "trend"
    CONFIRMATION = "confirmation"
    DIVERGENCE = "divergence"
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    PROFILE = "profile"


class ProfileLevelType(str, Enum):
    """
    Volume Profile level classifications.
    """

    POC = "poc"
    HVN = "hvn"
    LVN = "lvn"
    VALUE_HIGH = "value_high"
    VALUE_LOW = "value_low"


# =============================================================================
# VOLUME OBSERVATION
# =============================================================================


@dataclass
class VolumeObservation:
    """
    Represents volume information for a single candle.
    """

    index: int

    volume: float

    average_volume: float = 0.0

    relative_volume: float = 0.0

    state: VolumeState = VolumeState.NORMAL

    volume_type: VolumeType = VolumeType.UNKNOWN

    price_change: float = 0.0

    price_change_percent: float = 0.0

    direction: VolumeDirection = (
        VolumeDirection.NEUTRAL
    )

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# VOLUME SPIKE
# =============================================================================


@dataclass
class VolumeSpike:
    """
    Represents an abnormal increase in volume/activity.
    """

    index: int

    volume: float

    average_volume: float

    relative_volume: float

    state: VolumeState

    direction: VolumeDirection

    strength: float = 0.0

    confidence: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# VOLUME TREND
# =============================================================================


@dataclass
class VolumeTrend:
    """
    Represents the direction and behavior of volume over a lookback period.
    """

    direction: VolumeDirection = (
        VolumeDirection.NEUTRAL
    )

    state: VolumeState = VolumeState.NORMAL

    slope: float = 0.0

    current_volume: float = 0.0

    average_volume: float = 0.0

    relative_volume: float = 0.0

    rising: bool = False

    falling: bool = False

    stable: bool = False

    confidence: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# VOLUME CONFIRMATION
# =============================================================================


@dataclass
class VolumeConfirmation:
    """
    Determines whether volume supports a price movement.
    """

    confirmed: bool = False

    direction: VolumeDirection = (
        VolumeDirection.NEUTRAL
    )

    score: float = 0.0

    price_aligned: bool = False

    volume_aligned: bool = False

    spike_present: bool = False

    trend_aligned: bool = False

    divergence: bool = False

    reasons: list[str] = field(
        default_factory=list
    )


# =============================================================================
# VOLUME PROFILE LEVEL
# =============================================================================


@dataclass
class VolumeProfileLevel:
    """
    Represents a significant price level derived from volume distribution.
    """

    price: float

    volume: float

    level_type: ProfileLevelType

    strength: float = 0.0

    percentage_of_total: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# VOLUME PROFILE
# =============================================================================


@dataclass
class VolumeProfile:
    """
    Represents the complete volume distribution across price.
    """

    levels: list[VolumeProfileLevel] = field(
        default_factory=list
    )

    poc: float | None = None

    value_area_high: float | None = None

    value_area_low: float | None = None

    high_volume_nodes: list[
        VolumeProfileLevel
    ] = field(
        default_factory=list
    )

    low_volume_nodes: list[
        VolumeProfileLevel
    ] = field(
        default_factory=list
    )

    total_volume: float = 0.0

    confidence: float = 0.0


# =============================================================================
# ACCUMULATION
# =============================================================================


@dataclass
class AccumulationSignal:
    """
    Represents possible accumulation behavior.

    This is a heuristic signal and does not claim knowledge of institutional
    intent.
    """

    detected: bool = False

    direction: VolumeDirection = (
        VolumeDirection.BULLISH
    )

    score: float = 0.0

    confidence: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# DISTRIBUTION
# =============================================================================


@dataclass
class DistributionSignal:
    """
    Represents possible distribution behavior.

    This is a heuristic signal and does not claim knowledge of institutional
    intent.
    """

    detected: bool = False

    direction: VolumeDirection = (
        VolumeDirection.BEARISH
    )

    score: float = 0.0

    confidence: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )


# =============================================================================
# VOLUME ANALYSIS
# =============================================================================


@dataclass
class VolumeAnalysis:
    """
    Final output of the Volume Agent.
    """

    volume_type: VolumeType = VolumeType.UNKNOWN

    current_volume: float = 0.0

    average_volume: float = 0.0

    relative_volume: float = 0.0

    state: VolumeState = VolumeState.NORMAL

    direction: VolumeDirection = (
        VolumeDirection.NEUTRAL
    )

    confidence: float = 0.0

    probability: float = 0.0

    spikes: list[VolumeSpike] = field(
        default_factory=list
    )

    trend: VolumeTrend | None = None

    confirmation: VolumeConfirmation | None = None

    profile: VolumeProfile | None = None

    accumulation: AccumulationSignal | None = None

    distribution: DistributionSignal | None = None

    observations: list[
        VolumeObservation
    ] = field(
        default_factory=list
    )

    reasons: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
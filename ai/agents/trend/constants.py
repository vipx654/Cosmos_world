"""
===============================================================================
COSMOS Trend Agent Constants

Centralized configuration and thresholds for the Trend Agent.

All values in this module are intentionally kept in one place so the
Trend Agent can be calibrated without modifying detection engines.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations


# =============================================================================
# SWING DETECTION
# =============================================================================

# Minimum candle/index separation between meaningful swing points.
MIN_SWING_DISTANCE = 3

# Minimum number of structural points required before attempting
# reliable market-structure classification.
MIN_STRUCTURE_POINTS = 4

# Minimum number of candles required for a stable swing analysis.
MIN_SWING_CANDLES = 7

# Maximum number of recent swings normally retained for analysis.
MAX_SWING_POINTS = 100


# =============================================================================
# STRUCTURE
# =============================================================================

# Minimum number of classified structures before assigning a strong
# structural bias.
MIN_CONFIRMED_STRUCTURES = 3

# Number of recent structure points used for short-term trend classification.
STRUCTURE_LOOKBACK = 6

# Minimum structural agreement required before calling a directional trend.
STRUCTURE_AGREEMENT_RATIO = 0.60


# =============================================================================
# TREND SCORE REGIMES
# =============================================================================

STRONG_TREND_SCORE = 85.0

MEDIUM_TREND_SCORE = 65.0

WEAK_TREND_SCORE = 45.0

VERY_STRONG_TREND_SCORE = 92.0

MIN_ACTIONABLE_CONFIDENCE = 60.0


# =============================================================================
# EMA
# =============================================================================

EMA_FAST_PERIOD = 20

EMA_MEDIUM_PERIOD = 50

EMA_SLOW_PERIOD = 100

EMA_MAJOR_PERIOD = 200

EMA_COMPRESSION_THRESHOLD = 0.001

EMA_EXPANSION_THRESHOLD = 0.005

# Minimum relative EMA slope required to treat the movement as meaningful.
EMA_MIN_SLOPE_RATIO = 0.0001


# =============================================================================
# MOMENTUM
# =============================================================================

MOMENTUM_LOOKBACK = 14

MOMENTUM_FAST_LOOKBACK = 5

MOMENTUM_SLOW_LOOKBACK = 20

# Minimum normalized momentum required to classify expansion.
MOMENTUM_EXPANSION_THRESHOLD = 0.60

# Below this value momentum is considered weak/contracting.
MOMENTUM_CONTRACTION_THRESHOLD = 0.25

# Strong acceleration threshold.
MOMENTUM_ACCELERATION_THRESHOLD = 0.50

# Exhaustion threshold.
MOMENTUM_EXHAUSTION_THRESHOLD = 0.85


# =============================================================================
# TRENDLINE
# =============================================================================

MIN_TRENDLINE_TOUCHES = 2

PREFERRED_TRENDLINE_TOUCHES = 3

MAX_TRENDLINE_DISTANCE_RATIO = 0.003

TRENDLINE_BREAK_THRESHOLD = 0.001

TRENDLINE_RETEST_THRESHOLD = 0.0015

MIN_TRENDLINE_SLOPE = 0.000001


# =============================================================================
# CONFIDENCE WEIGHTS
# =============================================================================

STRUCTURE_WEIGHT = 0.30

MOMENTUM_WEIGHT = 0.25

EMA_WEIGHT = 0.20

TRENDLINE_WEIGHT = 0.15

CONFLUENCE_WEIGHT = 0.10


# =============================================================================
# CONFIDENCE PENALTIES
# =============================================================================

# Used when evidence conflicts.
CONFLICT_PENALTY = 10.0

# Used when insufficient market data exists.
LOW_SAMPLE_PENALTY = 15.0

# Used when trend evidence is highly mixed.
MIXED_STRUCTURE_PENALTY = 8.0

# Maximum penalty allowed.
MAX_CONFIDENCE_PENALTY = 30.0


# =============================================================================
# CONFIDENCE LIMITS
# =============================================================================

MIN_CONFIDENCE = 0.0

MAX_CONFIDENCE = 100.0


# =============================================================================
# CHART / EVIDENCE
# =============================================================================

# Evidence at or above this confidence can become confirmed.
EVIDENCE_CONFIRMATION_THRESHOLD = 65.0

# Evidence at or above this confidence can become locked,
# provided the corresponding engine marks it structurally valid.
EVIDENCE_LOCK_THRESHOLD = 80.0

# Evidence below this confidence should generally remain developing.
EVIDENCE_DEVELOPING_THRESHOLD = 45.0


# =============================================================================
# DATA QUALITY
# =============================================================================

# Minimum candles for basic trend analysis.
MIN_CANDLES = 20

# Minimum candles preferred for full EMA confirmation.
PREFERRED_CANDLES = 200

# Maximum allowed missing/invalid candles ratio.
MAX_INVALID_CANDLE_RATIO = 0.05


# =============================================================================
# NUMERICAL SAFETY
# =============================================================================

EPSILON = 1e-9
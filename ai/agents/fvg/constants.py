"""
===============================================================================
COSMOS Fair Value Gap Constants V2

Central configuration for FVG detection, lifecycle analysis, scoring,
confluence, ranking and inversion.

All scoring thresholds are deterministic and bounded to 0-100.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations


# =============================================================================
# ENGINE
# =============================================================================

ENGINE_VERSION = "2.0.0"

AGENT_NAME = "fvg"


# =============================================================================
# SCORE RANGES
# =============================================================================

MIN_SCORE = 0.0
MAX_SCORE = 100.0

MIN_CONFIDENCE = MIN_SCORE
MAX_CONFIDENCE = MAX_SCORE

MIN_PROBABILITY = MIN_SCORE
MAX_PROBABILITY = MAX_SCORE

MIN_STRENGTH = MIN_SCORE
MAX_STRENGTH = MAX_SCORE

MIN_QUALITY_SCORE = MIN_SCORE
MAX_QUALITY_SCORE = MAX_SCORE

MIN_RANKING_SCORE = MIN_SCORE
MAX_RANKING_SCORE = MAX_SCORE


# =============================================================================
# DEFAULT SCORES
# =============================================================================

DEFAULT_CONFIDENCE = 50.0
DEFAULT_PROBABILITY = 50.0
DEFAULT_STRENGTH = 50.0


# =============================================================================
# QUALITY LEVELS
# =============================================================================

VERY_LOW_QUALITY = 20.0
LOW_QUALITY = 40.0
MODERATE_QUALITY = 60.0
HIGH_QUALITY = 75.0
VERY_HIGH_QUALITY = 90.0
EXTREME_QUALITY = 95.0


# =============================================================================
# DETECTION
# =============================================================================

MIN_CANDLES_REQUIRED = 3

DEFAULT_LOOKBACK = 200

FVG_LOOKBACK = 100

MAX_FVG_COUNT = 200


# =============================================================================
# GAP SETTINGS
# =============================================================================

MIN_GAP_SIZE = 0.0

MIN_GAP_RATIO = 0.0

SIGNIFICANT_GAP_RATIO = 0.25

STRONG_GAP_RATIO = 0.50

EXTREME_GAP_RATIO = 1.00


# =============================================================================
# CANDLE QUALITY
# =============================================================================

MIN_BODY_RATIO = 0.50

STRONG_BODY_RATIO = 0.65

EXTREME_BODY_RATIO = 0.80


# =============================================================================
# DISPLACEMENT
# =============================================================================

MIN_DISPLACEMENT_SCORE = 0.0

DEFAULT_DISPLACEMENT_SCORE = 50.0

STRONG_DISPLACEMENT_SCORE = 70.0

EXTREME_DISPLACEMENT_SCORE = 85.0


# =============================================================================
# MITIGATION
# =============================================================================

PARTIAL_FILL_RATIO = 0.50

MIDPOINT_FILL_RATIO = 0.50

DEEP_FILL_RATIO = 0.75

FULL_FILL_RATIO = 1.00


# =============================================================================
# FVG AGE
# =============================================================================

MAX_FVG_AGE = 500

FRESH_MAX_AGE = 3

YOUNG_MAX_AGE = 10

MATURE_MAX_AGE = 50


# =============================================================================
# INVERSION / IFVG
# =============================================================================

INVERSION_CONFIRMATION_RATIO = 1.00

MIN_INVERSION_CONFIRMATION_CANDLES = 1

STRONG_INVERSION_CONFIRMATION_CANDLES = 2

MAX_INVERSION_CONFIRMATION_CANDLES = 3

INVERSION_CLOSE_BUFFER_RATIO = 0.0


# =============================================================================
# CONFIRMATION
# =============================================================================

MIN_CONFIRMATION_SCORE = 2

STRONG_CONFIRMATION_SCORE = 4

MAX_CONFIRMATION_SCORE = 5

MIN_CONFIRMATION_CONFIDENCE = 55.0

STRONG_CONFIRMATION_CONFIDENCE = 70.0

MIN_CONFIRMATION_PROBABILITY = 55.0

STRONG_CONFIRMATION_PROBABILITY = 70.0

MIN_CONFIRMATION_STRENGTH = 55.0

STRONG_CONFIRMATION_STRENGTH = 70.0


# =============================================================================
# CONFLUENCE WEIGHTS
# =============================================================================

TREND_WEIGHT = 0.10

MARKET_STRUCTURE_WEIGHT = 0.15

LIQUIDITY_WEIGHT = 0.10

SWEEP_WEIGHT = 0.15

ORDER_BLOCK_WEIGHT = 0.10

SMC_WEIGHT = 0.10

VOLUME_WEIGHT = 0.05

SESSION_WEIGHT = 0.05

HTF_WEIGHT = 0.10

DISPLACEMENT_WEIGHT = 0.10


# =============================================================================
# CONFLUENCE THRESHOLDS
# =============================================================================

MAX_CONFLUENCE_SCORE = 100.0

HIGH_CONFLUENCE_SCORE = 70.0

VERY_HIGH_CONFLUENCE_SCORE = 85.0

CONFLICT_PENALTY_MAX = 30.0


# =============================================================================
# PROBABILITY WEIGHTS
#
# This remains a heuristic score, not a statistically validated win rate.
# =============================================================================

PROBABILITY_BASE_WEIGHT = 0.20

PROBABILITY_STRENGTH_WEIGHT = 0.15

PROBABILITY_QUALITY_WEIGHT = 0.20

PROBABILITY_CONFLUENCE_WEIGHT = 0.30

PROBABILITY_FRESHNESS_WEIGHT = 0.05

PROBABILITY_DISPLACEMENT_WEIGHT = 0.10


# =============================================================================
# CONFIDENCE WEIGHTS
# =============================================================================

CONFIDENCE_QUALITY_WEIGHT = 0.30

CONFIDENCE_PROBABILITY_WEIGHT = 0.20

CONFIDENCE_CONFLUENCE_WEIGHT = 0.25

CONFIDENCE_STRENGTH_WEIGHT = 0.15

CONFIDENCE_VALIDITY_WEIGHT = 0.10


# =============================================================================
# RANKING WEIGHTS
# =============================================================================

RANKING_CONFIDENCE_WEIGHT = 0.20

RANKING_PROBABILITY_WEIGHT = 0.20

RANKING_QUALITY_WEIGHT = 0.20

RANKING_CONFLUENCE_WEIGHT = 0.25

RANKING_STRENGTH_WEIGHT = 0.10

RANKING_FRESHNESS_WEIGHT = 0.05


# =============================================================================
# DECISION THRESHOLDS
# =============================================================================

WATCH_THRESHOLD = 50.0

VALID_THRESHOLD = 65.0

HIGH_CONFLUENCE_THRESHOLD = 75.0

AVOID_THRESHOLD = 35.0


# =============================================================================
# MITIGATION PENALTIES / BONUSES
# =============================================================================

UNTOUCHED_BONUS = 5.0

PARTIAL_MITIGATION_PENALTY = 3.0

DEEP_MITIGATION_PENALTY = 8.0

FULL_FILL_PENALTY = 30.0

INVALIDATION_PENALTY = 40.0


# =============================================================================
# INVERSION PENALTIES
# =============================================================================

POTENTIAL_INVERSION_PENALTY = 3.0

CONFIRMED_INVERSION_PENALTY = 10.0


# =============================================================================
# EVIDENCE
# =============================================================================

MIN_EVIDENCE_FOR_BONUS = 2

STRONG_EVIDENCE_COUNT = 5

MAX_EVIDENCE_BONUS = 10.0


# =============================================================================
# PRICE PRECISION
# =============================================================================

DEFAULT_PRICE_PRECISION = 8


# =============================================================================
# DEFAULT METADATA
# =============================================================================

DEFAULT_TIMEFRAME = "UNKNOWN"

DEFAULT_SOURCE = "FVGEngine"


# =============================================================================
# FVG TYPES
# =============================================================================

BULLISH_FVG = "BULLISH"

BEARISH_FVG = "BEARISH"

INVERSION_FVG = "INVERSION"


# =============================================================================
# FVG STATUS
# =============================================================================

FRESH = "FRESH"

TESTED = "TESTED"

PARTIAL = "PARTIAL"

FILLED = "FILLED"

INVALID = "INVALID"


# =============================================================================
# SAFETY
# =============================================================================

MIN_FINITE_PRICE = 0.0

EPSILON = 1e-12
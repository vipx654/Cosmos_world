"""
===============================================================================
COSMOS Liquidity Constants

Institutional liquidity detection constants.

Author: COSMOS Development Team
License: MIT
Version: 2.0.0
===============================================================================
"""


# =============================================================================
# Equal Level Detection
# =============================================================================

LIQUIDITY_TOLERANCE = 0.00005

MIN_TOUCHES = 2

MAX_TOUCHES = 10


# =============================================================================
# Adaptive Liquidity Detection
# =============================================================================

MIN_LIQUIDITY_STRENGTH = 0.0

MAX_LIQUIDITY_STRENGTH = 100.0

MIN_LIQUIDITY_CONFIDENCE = 0.0

MAX_LIQUIDITY_CONFIDENCE = 100.0

MIN_LIQUIDITY_QUALITY = 0.0

MAX_LIQUIDITY_QUALITY = 100.0


# =============================================================================
# Cluster Detection
# =============================================================================

CLUSTER_DISTANCE = 0.00020

MIN_CLUSTER_LEVELS = 3

MAX_CLUSTER_LEVELS = 50

CLUSTER_CENTER_WEIGHT = 1.0

CLUSTER_STRENGTH_WEIGHT = 1.0

CLUSTER_CONFIDENCE_WEIGHT = 1.0


# =============================================================================
# Liquidity Strength
# =============================================================================

MAX_AGE = 300

FRESH_LIQUIDITY_AGE = 30

ACTIVE_LIQUIDITY_AGE = 100

AGING_LIQUIDITY_AGE = 200

STALE_LIQUIDITY_AGE = MAX_AGE


# =============================================================================
# Touch Scoring
# =============================================================================

TOUCH_WEIGHT = 12.0

MAX_TOUCH_SCORE = 40.0

THREE_TOUCH_BONUS = 5.0

FOUR_TOUCH_BONUS = 10.0

FIVE_PLUS_TOUCH_BONUS = 15.0


# =============================================================================
# Strength Scoring
# =============================================================================

STRENGTH_WEIGHT = 0.30

MAX_STRENGTH_SCORE = 30.0


# =============================================================================
# Confidence Scoring
# =============================================================================

CONFIDENCE_WEIGHT = 0.30

MAX_CONFIDENCE_SCORE = 30.0


# =============================================================================
# Quality Scoring
# =============================================================================

QUALITY_WEIGHT = 0.30

MAX_QUALITY_SCORE = 100.0


# =============================================================================
# Freshness Scoring
# =============================================================================

FRESHNESS_FRESH_SCORE = 100.0

FRESHNESS_ACTIVE_SCORE = 80.0

FRESHNESS_AGING_SCORE = 55.0

FRESHNESS_STALE_SCORE = 25.0


# =============================================================================
# Age Decay
# =============================================================================

AGE_DECAY_START = 30

AGE_DECAY_RATE = 0.15

MIN_AGE_FACTOR = 0.25


# =============================================================================
# Distance Scoring
# =============================================================================

DISTANCE_WEIGHT = 0.20

MAX_DISTANCE_SCORE = 100.0

NEAR_LIQUIDITY_DISTANCE = 0.00100

MEDIUM_LIQUIDITY_DISTANCE = 0.00300

FAR_LIQUIDITY_DISTANCE = 0.00600


# =============================================================================
# Sweep Probability
# =============================================================================

BASE_SWEEP_PROBABILITY = 25.0

TOUCH_SWEEP_WEIGHT = 5.0

STRENGTH_SWEEP_WEIGHT = 0.20

CONFIDENCE_SWEEP_WEIGHT = 0.20

QUALITY_SWEEP_WEIGHT = 0.20

CONFLUENCE_SWEEP_WEIGHT = 0.20

DISTANCE_SWEEP_WEIGHT = 0.15

FRESHNESS_SWEEP_WEIGHT = 0.15

MAX_SWEEP_PROBABILITY = 100.0

MIN_SWEEP_PROBABILITY = 0.0


# =============================================================================
# Sweep Classification Thresholds
# =============================================================================

SWEEP_VERY_LOW_THRESHOLD = 20.0

SWEEP_LOW_THRESHOLD = 40.0

SWEEP_MODERATE_THRESHOLD = 60.0

SWEEP_HIGH_THRESHOLD = 80.0

SWEEP_VERY_HIGH_THRESHOLD = 100.0


# =============================================================================
# Mitigation
# =============================================================================

MIN_MITIGATION = 0.0

MAX_MITIGATION = 100.0

PARTIAL_MITIGATION_THRESHOLD = 25.0

HIGH_MITIGATION_THRESHOLD = 60.0

FULL_MITIGATION_THRESHOLD = 90.0


# =============================================================================
# Confluence
# =============================================================================

MAX_CONFLUENCE_SCORE = 100.0

CONFLUENCE_TREND_WEIGHT = 20.0

CONFLUENCE_STRUCTURE_WEIGHT = 20.0

CONFLUENCE_SMC_WEIGHT = 20.0

CONFLUENCE_ORDER_BLOCK_WEIGHT = 15.0

CONFLUENCE_FVG_WEIGHT = 10.0

CONFLUENCE_SWEEP_WEIGHT = 15.0


# =============================================================================
# Liquidity Priority
# =============================================================================

PRIORITY_STRENGTH_WEIGHT = 0.20

PRIORITY_CONFIDENCE_WEIGHT = 0.20

PRIORITY_QUALITY_WEIGHT = 0.20

PRIORITY_SWEEP_WEIGHT = 0.20

PRIORITY_CONFLUENCE_WEIGHT = 0.20

MAX_PRIORITY = 100.0


# =============================================================================
# Target Ranking
# =============================================================================

TARGET_STRENGTH_WEIGHT = 0.20

TARGET_DISTANCE_WEIGHT = 0.20

TARGET_SWEEP_WEIGHT = 0.25

TARGET_QUALITY_WEIGHT = 0.15

TARGET_CONFLUENCE_WEIGHT = 0.20

MAX_TARGET_SCORE = 100.0


# =============================================================================
# Directional Bias
# =============================================================================

BULLISH_LIQUIDITY_WEIGHT = 1.0

BEARISH_LIQUIDITY_WEIGHT = 1.0

DIRECTIONAL_BIAS_THRESHOLD = 10.0


# =============================================================================
# External Liquidity
# =============================================================================

EXTERNAL_STRENGTH = 90.0

EXTERNAL_CONFIDENCE = 90.0


# =============================================================================
# Internal Liquidity
# =============================================================================

INTERNAL_STRENGTH = 50.0

INTERNAL_CONFIDENCE = 55.0


# =============================================================================
# Equal High / Equal Low Defaults
# =============================================================================

EQUAL_LEVEL_BASE_CONFIDENCE = 60.0

EQUAL_LEVEL_TOUCH_CONFIDENCE = 10.0

EQUAL_LEVEL_STRENGTH_PER_TOUCH = 20.0


# =============================================================================
# Ranking Limits
# =============================================================================

MAX_NEAREST_TARGETS = 5

MAX_STRONGEST_LEVELS = 5

MAX_SWEEP_CANDIDATES = 5


# =============================================================================
# Chart Integration
# =============================================================================

LIQUIDITY_ANNOTATION_PREFIX = "liquidity"

CLUSTER_ANNOTATION_PREFIX = "liquidity_cluster"

LOCKED_LIQUIDITY_MIN_CONFIDENCE = 75.0


# =============================================================================
# Confidence Weights
# =============================================================================
#
# Existing weights preserved for backward compatibility.
# Total = 100.
# =============================================================================

WEIGHT_BUY_SIDE = 20

WEIGHT_SELL_SIDE = 20

WEIGHT_INTERNAL = 15

WEIGHT_EXTERNAL = 15

WEIGHT_CLUSTER = 15

WEIGHT_QUALITY = 15


# =============================================================================
# Engine Limits
# =============================================================================

MAX_LIQUIDITY_LEVELS = 500

MAX_LIQUIDITY_CLUSTERS = 100

MAX_EVIDENCE_ITEMS = 50

MAX_CONFLUENCE_FACTORS = 20
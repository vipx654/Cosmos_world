"""
===============================================================================
COSMOS Volume Agent Constants

Configuration and thresholds for volume analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations


# =============================================================================
# ENGINE
# =============================================================================

ENGINE_VERSION = "1.0.0"

AGENT_NAME = "volume"


# =============================================================================
# LOOKBACK
# =============================================================================

DEFAULT_LOOKBACK = 20

MIN_LOOKBACK = 5

MAX_LOOKBACK = 500


# =============================================================================
# RELATIVE VOLUME
# =============================================================================

# Relative volume:
#
#     current_volume / average_volume
#
# Example:
#
#     2.0 = current volume is twice the average.
#

LOW_RELATIVE_VOLUME = 0.50

NORMAL_RELATIVE_VOLUME = 1.00

HIGH_RELATIVE_VOLUME = 1.50

SPIKE_RELATIVE_VOLUME = 2.00

EXTREME_RELATIVE_VOLUME = 3.00


# =============================================================================
# VOLUME STATES
# =============================================================================

VERY_LOW_VOLUME = 0.50

LOW_VOLUME = 0.75

NORMAL_VOLUME = 1.25

HIGH_VOLUME = 2.00

EXTREME_VOLUME = 3.00


# =============================================================================
# SPIKE DETECTION
# =============================================================================

MIN_SPIKE_RELATIVE_VOLUME = 1.50

STRONG_SPIKE_RELATIVE_VOLUME = 2.00

EXTREME_SPIKE_RELATIVE_VOLUME = 3.00


# =============================================================================
# VOLUME TREND
# =============================================================================

TREND_MIN_CHANGE = 0.05

TREND_STRONG_CHANGE = 0.15


# =============================================================================
# PRICE / VOLUME CONFIRMATION
# =============================================================================

MIN_CONFIRMATION_SCORE = 2

STRONG_CONFIRMATION_SCORE = 4

MAX_CONFIRMATION_SCORE = 5


# =============================================================================
# ACCUMULATION / DISTRIBUTION
# =============================================================================

MIN_ACCUMULATION_SCORE = 3

MIN_DISTRIBUTION_SCORE = 3

STRONG_ACCUMULATION_SCORE = 5

STRONG_DISTRIBUTION_SCORE = 5


# =============================================================================
# PROBABILITY
# =============================================================================

MIN_PROBABILITY = 0.0

DEFAULT_PROBABILITY = 50.0

HIGH_PROBABILITY = 70.0

VERY_HIGH_PROBABILITY = 85.0

MAX_PROBABILITY = 100.0


# =============================================================================
# CONFIDENCE
# =============================================================================

MIN_CONFIDENCE = 0.0

DEFAULT_CONFIDENCE = 50.0

HIGH_CONFIDENCE = 70.0

VERY_HIGH_CONFIDENCE = 85.0

MAX_CONFIDENCE = 100.0


# =============================================================================
# VOLUME PROFILE
# =============================================================================

# Default number of price rows used when constructing a simple profile.

DEFAULT_PROFILE_ROWS = 24

MIN_PROFILE_ROWS = 5

MAX_PROFILE_ROWS = 200


# Typical value-area percentage.

DEFAULT_VALUE_AREA_PERCENT = 70.0


# Node thresholds relative to the profile's average row volume.

HVN_THRESHOLD = 1.50

STRONG_HVN_THRESHOLD = 2.00

LVN_THRESHOLD = 0.50


# =============================================================================
# PRICE MOVEMENT
# =============================================================================

MIN_PRICE_CHANGE = 0.0

SIGNIFICANT_PRICE_CHANGE = 0.001

STRONG_PRICE_CHANGE = 0.002


# =============================================================================
# DIVERGENCE
# =============================================================================

DIVERGENCE_LOOKBACK = 10

MIN_DIVERGENCE_CHANGE = 0.05


# =============================================================================
# DATA TYPE
# =============================================================================

DEFAULT_VOLUME_TYPE = "tick"

TICK_VOLUME = "tick"

REAL_VOLUME = "real"

UNKNOWN_VOLUME = "unknown"


# =============================================================================
# DEFAULT SOURCE
# =============================================================================

DEFAULT_SOURCE = "VolumeEngine"
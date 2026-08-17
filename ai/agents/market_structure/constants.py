"""
===============================================================================
COSMOS Market Structure Constants

Institutional market structure thresholds and confidence parameters.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

# =============================================================================
# STRUCTURAL DISTANCE
# =============================================================================

MIN_BOS_DISTANCE = 2

MIN_CHOCH_DISTANCE = 2

MIN_MSS_DISTANCE = 2


# =============================================================================
# STRUCTURAL BREAK VALIDATION
# =============================================================================

# Minimum price displacement required to consider a break meaningful.
MIN_BREAK_DISPLACEMENT = 0.0

# Minimum structural strength required for a validated event.
MIN_STRUCTURE_STRENGTH = 50.0

# Minimum confidence required for a confirmed structural event.
MIN_EVENT_CONFIDENCE = 50.0


# =============================================================================
# PROTECTED LEVELS
# =============================================================================

# Minimum number of structural observations required before
# treating a high/low as a protected structural level.
MIN_PROTECTED_LEVELS = 2

# Maximum number of recent swings considered when determining
# protected structural levels.
PROTECTED_SWING_LOOKBACK = 20


# =============================================================================
# EVENT CONFIDENCE
# =============================================================================

CONFIDENCE_BONUS_BOS = 20

CONFIDENCE_BONUS_CHOCH = 25

CONFIDENCE_BONUS_MSS = 30


# =============================================================================
# EVENT WEIGHTS
# =============================================================================

WEIGHT_BOS = 0.35

WEIGHT_CHOCH = 0.20

WEIGHT_MSS = 0.20

WEIGHT_INTERNAL = 0.15

WEIGHT_EXTERNAL = 0.10


# =============================================================================
# STRUCTURE AGREEMENT
# =============================================================================

# Bonus when internal and external structure agree.
STRUCTURE_AGREEMENT_BONUS = 10.0

# Penalty when internal and external structure conflict.
STRUCTURE_CONFLICT_PENALTY = 15.0

# Penalty when bullish and bearish structural events occur simultaneously.
EVENT_CONFLICT_PENALTY = 20.0


# =============================================================================
# STRUCTURE STRENGTH
# =============================================================================

MAX_STRUCTURE_STRENGTH = 100.0

MAX_EVENT_CONFIDENCE = 100.0

MAX_FINAL_CONFIDENCE = 100.0


# =============================================================================
# RECENCY
# =============================================================================

# Number of latest swings considered most relevant for current structure.
RECENT_SWING_LOOKBACK = 10


# =============================================================================
# SAFETY
# =============================================================================

MIN_SWINGS_FOR_STRUCTURE = 4

MIN_SWINGS_FOR_CHOCH = 6

MIN_SWINGS_FOR_MSS = 6
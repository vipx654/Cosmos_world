"""
===============================================================================
COSMOS Trap Agent Constants

Shared thresholds for false-breakout and liquidity-trap detection.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations


# =============================================================================
# LOOKBACK
# =============================================================================

DEFAULT_LOOKBACK = 20

MIN_LOOKBACK = 5


# =============================================================================
# RECLAIM / FAILURE TIMING
# =============================================================================

# Maximum number of candles allowed between the breakout and reclaim.
#
# A quick reclaim is more consistent with a failed breakout than a delayed
# structural reversal.
MAX_RECLAIM_BARS = 3


# Minimum number of observations required before evaluating a trap.
MIN_CANDLES_REQUIRED = 5


# =============================================================================
# BREAKOUT
# =============================================================================

# Minimum extension beyond the reference level as a fraction of the
# breakout candle's range.
MIN_BREAK_DISTANCE_RATIO = 0.10


# Prevent tiny price violations from being classified as meaningful breaks.
MIN_EXTENSION_RATIO = 0.05


# =============================================================================
# RECLAIM
# =============================================================================

# Minimum percentage of the broken level's side that price must reclaim.
RECLAIM_THRESHOLD = 0.50


# =============================================================================
# CANDLE CLOSE POSITION
# =============================================================================

# Bull trap:
#
# Price breaks above resistance but closes back toward the lower part
# of the breakout candle.
BULL_TRAP_CLOSE_THRESHOLD = 0.40


# Bear trap:
#
# Price breaks below support but closes back toward the upper part
# of the breakout candle.
BEAR_TRAP_CLOSE_THRESHOLD = 0.60


# =============================================================================
# WICK / REJECTION
# =============================================================================

MIN_REJECTION_WICK_RATIO = 0.35

STRONG_REJECTION_WICK_RATIO = 0.55


# =============================================================================
# VOLUME / ACTIVITY
# =============================================================================

# Relative-volume thresholds.
#
# These are contextual thresholds, not universal market laws.
MIN_TRAP_RVOL = 1.20

STRONG_TRAP_RVOL = 1.50

EXTREME_TRAP_RVOL = 2.00


# =============================================================================
# FOLLOW-THROUGH
# =============================================================================

# Minimum continuation failure required before assigning follow-through
# failure evidence.
MIN_FOLLOW_THROUGH_RATIO = 0.10

STRONG_FOLLOW_THROUGH_RATIO = 0.25


# =============================================================================
# SCORING
# =============================================================================

# Six primary evidence components:
#
#   1. Breakout
#   2. Reclaim
#   3. Rejection
#   4. Volume
#   5. Follow-through failure
#   6. Structure/context
#
MAX_TRAP_SCORE = 6.0

MIN_TRAP_SCORE = 3.0

STRONG_TRAP_SCORE = 5.0


# =============================================================================
# SCORE WEIGHTS
# =============================================================================

BREAKOUT_WEIGHT = 1.0

RECLAIM_WEIGHT = 1.0

REJECTION_WEIGHT = 1.0

VOLUME_WEIGHT = 1.0

FOLLOW_THROUGH_FAILURE_WEIGHT = 1.0

STRUCTURE_WEIGHT = 1.0


# =============================================================================
# PROBABILITY
# =============================================================================

DEFAULT_TRAP_PROBABILITY = 50.0

HIGH_TRAP_PROBABILITY = 70.0

VERY_HIGH_TRAP_PROBABILITY = 85.0


# =============================================================================
# CONFIDENCE
# =============================================================================

DEFAULT_TRAP_CONFIDENCE = 25.0

HIGH_TRAP_CONFIDENCE = 70.0

VERY_HIGH_TRAP_CONFIDENCE = 85.0


# =============================================================================
# PRICE / RANGE SAFETY
# =============================================================================

# Used to avoid division by zero or unstable calculations on zero-range
# candles.
MIN_CANDLE_RANGE = 1e-12


# =============================================================================
# CONFIDENCE PENALTIES
# =============================================================================

# Applied when contradictory evidence is detected.
CONFLICT_PENALTY = 10.0


# =============================================================================
# EVIDENCE LIMITS
# =============================================================================

# Maximum number of recent spikes/candles considered by secondary
# confirmation logic.
RECENT_EVIDENCE_BARS = 5
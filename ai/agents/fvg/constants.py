"""
===============================================================================
COSMOS Fair Value Gap Constants

Configuration and thresholds for FVG detection and analysis.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations


# =============================================================================
# ENGINE
# =============================================================================

ENGINE_VERSION = "1.0.0"

AGENT_NAME = "fvg"


# =============================================================================
# SCORE RANGES
# =============================================================================

MIN_CONFIDENCE = 0.0

DEFAULT_CONFIDENCE = 50.0

HIGH_CONFIDENCE = 80.0

MAX_CONFIDENCE = 100.0


MIN_PROBABILITY = 0.0

DEFAULT_PROBABILITY = 50.0

HIGH_PROBABILITY = 80.0

MAX_PROBABILITY = 100.0


MIN_STRENGTH = 0.0

DEFAULT_STRENGTH = 50.0

HIGH_STRENGTH = 80.0

MAX_STRENGTH = 100.0


# =============================================================================
# DETECTION
# =============================================================================

MIN_CANDLES_REQUIRED = 3

DEFAULT_LOOKBACK = 200

FVG_LOOKBACK = 100


# =============================================================================
# GAP SETTINGS
# =============================================================================

MIN_GAP_SIZE = 0.0

MIN_GAP_RATIO = 0.0

SIGNIFICANT_GAP_RATIO = 0.25

STRONG_GAP_RATIO = 0.50

MIN_BODY_RATIO = 0.50

# =============================================================================
# MITIGATION
# =============================================================================

PARTIAL_FILL_RATIO = 0.50

FULL_FILL_RATIO = 1.00


# =============================================================================
# INVERSION
# =============================================================================

INVERSION_CONFIRMATION_RATIO = 1.00

MIN_INVERSION_CONFIRMATION_CANDLES = 1


# =============================================================================
# CONFIRMATION
# =============================================================================

MIN_CONFIRMATION_SCORE = 2

STRONG_CONFIRMATION_SCORE = 4

MAX_CONFIRMATION_SCORE = 5


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
# DEFAULTS
# =============================================================================

DEFAULT_TIMEFRAME = "UNKNOWN"

DEFAULT_SOURCE = "FVGEngine"
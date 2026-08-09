"""
===============================================================================
COSMOS Session Agent

Determines the active FX market session and session quality.

Design:
    - Uses UTC internally.
    - Uses zoneinfo/IANA time zones for DST-aware session boundaries.
    - Never assumes broker-server time.
    - Session classification is contextual evidence, NOT a trade signal.

Author: COSMOS Development Team
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from enum import Enum
from zoneinfo import ZoneInfo


# =============================================================================
# ENUMS
# =============================================================================

class MarketSession(str, Enum):
    SYDNEY = "sydney"
    TOKYO = "tokyo"
    LONDON = "london"
    NEW_YORK = "new_york"
    LONDON_NEW_YORK_OVERLAP = "london_new_york_overlap"
    TOKYO_LONDON_OVERLAP = "tokyo_london_overlap"
    OFF_HOURS = "off_hours"


class SessionQuality(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    PEAK = "peak"


# =============================================================================
# RESULT
# =============================================================================

@dataclass
class SessionResult:
    """
    Standard output consumed by Strategy/Risk agents.
    """

    session: MarketSession = (
        MarketSession.OFF_HOURS
    )

    quality: SessionQuality = (
        SessionQuality.LOW
    )

    active: bool = False

    tradable: bool = False

    liquidity_score: float = 0.0

    volatility_score: float = 0.0

    session_score: float = 0.0

    timestamp_utc: str = ""

    local_times: dict[str, str] = field(
        default_factory=dict
    )

    warnings: list[str] = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )


# =============================================================================
# SESSION ENGINE
# =============================================================================

class SessionEngine:
    """
    DST-aware FX session classifier.

    Local exchange/session windows:

        Sydney:
            08:00 - 17:00 Australia/Sydney

        Tokyo:
            09:00 - 18:00 Asia/Tokyo

        London:
            08:00 - 17:00 Europe/London

        New York:
            08:00 - 17:00 America/New_York

    Overlaps are derived dynamically from those local windows.

    This avoids hard-coded UTC offsets.
    """

    SYDNEY = ZoneInfo(
        "Australia/Sydney"
    )

    TOKYO = ZoneInfo(
        "Asia/Tokyo"
    )

    LONDON = ZoneInfo(
        "Europe/London"
    )

    NEW_YORK = ZoneInfo(
        "America/New_York"
    )

    # Session quality is deliberately conservative.
    SESSION_PROFILES = {

        MarketSession.SYDNEY: (
            45.0,
            40.0,
        ),

        MarketSession.TOKYO: (
            55.0,
            50.0,
        ),

        MarketSession.LONDON: (
            80.0,
            80.0,
        ),

        MarketSession.NEW_YORK: (
            85.0,
            85.0,
        ),

        MarketSession.TOKYO_LONDON_OVERLAP: (
            70.0,
            70.0,
        ),

        MarketSession.LONDON_NEW_YORK_OVERLAP: (
            95.0,
            95.0,
        ),

        MarketSession.OFF_HOURS: (
            15.0,
            15.0,
        ),
    }

    # =========================================================================
    # MAIN API
    # =========================================================================

    def analyze(
        self,
        timestamp: datetime | None = None,
        symbol: str | None = None,
    ) -> SessionResult:
        """
        Determine current market session.

        `timestamp` may be:
            - timezone-aware datetime
            - naive datetime, interpreted as UTC
            - None, meaning current UTC time
        """

        dt_utc = self._to_utc(
            timestamp
        )

        sydney = self._in_session(
            dt_utc,
            self.SYDNEY,
        )

        tokyo = self._in_session(
            dt_utc,
            self.TOKYO,
        )

        london = self._in_session(
            dt_utc,
            self.LONDON,
        )

        new_york = self._in_session(
            dt_utc,
            self.NEW_YORK,
        )

        # =====================================================================
        # OVERLAPS
        # =====================================================================

        if tokyo and london:

            session = (
                MarketSession.TOKYO_LONDON_OVERLAP
            )

        elif london and new_york:

            session = (
                MarketSession.LONDON_NEW_YORK_OVERLAP
            )

        elif london:

            session = MarketSession.LONDON

        elif new_york:

            session = MarketSession.NEW_YORK

        elif tokyo:

            session = MarketSession.TOKYO

        elif sydney:

            session = MarketSession.SYDNEY

        else:

            session = MarketSession.OFF_HOURS

        liquidity, volatility = (
            self.SESSION_PROFILES[
                session
            ]
        )

        # =====================================================================
        # QUALITY
        # =====================================================================

        quality = (
            self._quality(
                liquidity,
                volatility,
            )
        )

        # =====================================================================
        # TRADABILITY
        # =====================================================================

        tradable = (
            session
            !=
            MarketSession.OFF_HOURS
            and
            liquidity >= 45.0
        )

        warnings: list[str] = []

        if session == MarketSession.OFF_HOURS:

            warnings.append(
                "Market activity is outside the primary FX sessions"
            )

        if session == MarketSession.LONDON_NEW_YORK_OVERLAP:

            warnings.append(
                "Peak liquidity/volatility window: execution may be fast"
            )

        # =====================================================================
        # SYMBOL CONTEXT
        # =====================================================================

        if symbol:

            symbol_upper = symbol.upper()

            if (
                "JPY" in symbol_upper
                and
                session
                == MarketSession.TOKYO
            ):

                liquidity = min(
                    100.0,
                    liquidity + 10.0,
                )

            if (
                (
                    "EUR" in symbol_upper
                    or
                    "GBP" in symbol_upper
                )
                and
                session
                in (
                    MarketSession.LONDON,
                    MarketSession.TOKYO_LONDON_OVERLAP,
                )
            ):

                liquidity = min(
                    100.0,
                    liquidity + 8.0,
                )

            if (
                "USD" in symbol_upper
                and
                session
                in (
                    MarketSession.NEW_YORK,
                    MarketSession.LONDON_NEW_YORK_OVERLAP,
                )
            ):

                liquidity = min(
                    100.0,
                    liquidity + 8.0,
                )

        # =====================================================================
        # SESSION SCORE
        # =====================================================================

        session_score = (
            liquidity * 0.55
            +
            volatility * 0.45
        )

        return SessionResult(

            session=session,

            quality=quality,

            active=(
                session
                !=
                MarketSession.OFF_HOURS
            ),

            tradable=tradable,

            liquidity_score=round(
                liquidity,
                2,
            ),

            volatility_score=round(
                volatility,
                2,
            ),

            session_score=round(
                session_score,
                2,
            ),

            timestamp_utc=(
                dt_utc.isoformat()
            ),

            local_times={
                "sydney": dt_utc.astimezone(
                    self.SYDNEY
                ).isoformat(),

                "tokyo": dt_utc.astimezone(
                    self.TOKYO
                ).isoformat(),

                "london": dt_utc.astimezone(
                    self.LONDON
                ).isoformat(),

                "new_york": dt_utc.astimezone(
                    self.NEW_YORK
                ).isoformat(),
            },

            warnings=warnings,

            metadata={
                "symbol": symbol,
                "timezone_source": "IANA",
                "dst_aware": True,
            },
        )

    # =========================================================================
    # SESSION WINDOW
    # =========================================================================

    @staticmethod
    def _in_session(
        dt_utc: datetime,
        zone: ZoneInfo,
    ) -> bool:

        local = dt_utc.astimezone(
            zone
        )

        current = local.time()

        start = time(
            8,
            0,
        )

        end = time(
            17,
            0,
        )

        return (
            start
            <=
            current
            <
            end
        )

    # =========================================================================
    # UTC NORMALIZATION
    # =========================================================================

    @staticmethod
    def _to_utc(
        timestamp: datetime | None,
    ) -> datetime:

        if timestamp is None:

            return datetime.now(
                timezone.utc
            )

        if timestamp.tzinfo is None:

            # COSMOS convention:
            # naive timestamps are interpreted as UTC.
            timestamp = timestamp.replace(
                tzinfo=timezone.utc
            )

        return timestamp.astimezone(
            timezone.utc
        )

    # =========================================================================
    # QUALITY
    # =========================================================================

    @staticmethod
    def _quality(
        liquidity: float,
        volatility: float,
    ) -> SessionQuality:

        score = (
            liquidity * 0.55
            +
            volatility * 0.45
        )

        if score >= 90.0:

            return SessionQuality.PEAK

        if score >= 75.0:

            return SessionQuality.HIGH

        if score >= 45.0:

            return SessionQuality.MODERATE

        return SessionQuality.LOW


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

session_engine = SessionEngine()


# =============================================================================
# PUBLIC API
# =============================================================================

def analyze_session(
    timestamp: datetime | None = None,
    symbol: str | None = None,
) -> SessionResult:

    return session_engine.analyze(
        timestamp=timestamp,
        symbol=symbol,
    )
"""
===============================================================================
COSMOS Session Sweep Engine

Production session classification for institutional liquidity sweeps.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from datetime import datetime
from numbers import Real

from ai.agents.sweep.constants import (
    ASIAN_SESSION,
    LONDON_SESSION,
    NEW_YORK_SESSION,
)
from ai.agents.sweep.models import SweepObject


class SessionSweepEngine:
    """
    Assigns each sweep to a trading session.

    V1 session model
    ----------------
    ASIAN       : 00:00 - 07:59
    LONDON      : 08:00 - 12:59
    NEW_YORK    : 13:00 - 21:59
    AFTER_HOURS : 22:00 - 23:59

    Notes
    -----
    Session boundaries are intentionally expressed in the timezone of the
    supplied candle timestamps. The engine does not guess a timezone or
    silently convert timestamps.

    V2 can add:

    • Kill zones
    • London/New York overlap
    • Session weighting
    • Session probability
    • Historical session statistics
    • DST-aware session calendars
    """

    AFTER_HOURS_SESSION = "AFTER_HOURS"

    def analyze(
        self,
        sweeps: list[SweepObject],
        candles,
    ) -> list[SweepObject]:
        """
        Assign trading-session metadata to detected sweeps.

        The input sweep objects are enriched in place and returned.
        """

        if not sweeps:
            return sweeps

        if candles is None:
            return sweeps

        try:
            candle_count = len(candles)
        except TypeError:
            return sweeps

        if candle_count == 0:
            return sweeps

        for sweep in sweeps:

            if not isinstance(
                sweep,
                SweepObject,
            ):
                continue

            candle_index = sweep.candle_index

            if not isinstance(
                candle_index,
                int,
            ):
                continue

            if candle_index < 0:
                continue

            if candle_index >= candle_count:
                continue

            candle = candles[candle_index]

            timestamp = self._get_timestamp(
                candle
            )

            if timestamp is None:
                continue

            session = self._classify_timestamp(
                timestamp
            )

            if session is None:
                continue

            sweep.session = session
            sweep.timestamp = timestamp

            sweep.add_evidence(
                f"{self._display_name(session)} Session Sweep"
            )

        return sweeps

    # =========================================================================
    # TIMESTAMP
    # =========================================================================

    @staticmethod
    def _get_timestamp(
        candle,
    ) -> datetime | None:
        """
        Extract a candle timestamp.

        COSMOS MarketCandle uses `timestamp`.

        `time` is also supported for compatibility with external candle
        implementations.
        """

        timestamp = getattr(
            candle,
            "timestamp",
            None,
        )

        if timestamp is None:
            timestamp = getattr(
                candle,
                "time",
                None,
            )

        if isinstance(
            timestamp,
            datetime,
        ):
            return timestamp

        if isinstance(
            timestamp,
            Real,
        ):
            try:
                return datetime.fromtimestamp(
                    float(timestamp)
                )
            except (
                OverflowError,
                OSError,
                ValueError,
            ):
                return None

        return None

    # =========================================================================
    # SESSION CLASSIFICATION
    # =========================================================================

    @classmethod
    def _classify_timestamp(
        cls,
        timestamp: datetime,
    ) -> str | None:
        """
        Classify a timestamp using its local hour.

        The timezone attached to an aware datetime is preserved. No implicit
        timezone conversion is performed in V1.
        """

        hour = timestamp.hour

        if 0 <= hour < 8:
            return ASIAN_SESSION

        if 8 <= hour < 13:
            return LONDON_SESSION

        if 13 <= hour < 22:
            return NEW_YORK_SESSION

        return cls.AFTER_HOURS_SESSION

    # =========================================================================
    # DISPLAY
    # =========================================================================

    @classmethod
    def _display_name(
        cls,
        session: str,
    ) -> str:
        """Convert internal session names into evidence labels."""

        names = {
            ASIAN_SESSION: "Asian",
            LONDON_SESSION: "London",
            NEW_YORK_SESSION: "New York",
            cls.AFTER_HOURS_SESSION: "After Hours",
        }

        return names.get(
            session,
            session.replace(
                "_",
                " ",
            ).title(),
        )
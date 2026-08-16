"""
===============================================================================
COSMOS Swing Engine

Production-grade market-structure swing detection.

Responsibilities
----------------
- Detect confirmed swing highs and swing lows.
- Filter duplicate and noisy structural points.
- Resolve competing same-type swings.
- Support configurable structural sensitivity.
- Apply optional price-distance filtering.
- Preserve deterministic chronological ordering.
- Preserve the existing SwingPoint interface.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.models import MarketCandle
from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.trend.constants import (
    MIN_SWING_DISTANCE,
    MIN_SWING_CANDLES,
)


# =============================================================================
# CONFIGURATION
# =============================================================================


@dataclass(frozen=True, slots=True)
class SwingConfig:
    """
    Configuration for swing detection.
    """

    lookback: int = 3

    min_distance: int = MIN_SWING_DISTANCE

    min_price_distance: float = 0.0

    strict: bool = True

    max_swings: int = 100


# =============================================================================
# ENGINE
# =============================================================================


class SwingEngine:
    """
    Structural swing detector.

    A swing is confirmed only when sufficient candles exist on both
    sides of the candidate.

    The output remains compatible with:

    - Market Structure
    - Liquidity
    - SMC
    - BOS
    - CHOCH
    - Dealing Range
    - Inducement
    """

    def __init__(
        self,
        lookback: int = 3,
        min_distance: int = MIN_SWING_DISTANCE,
        min_price_distance: float = 0.0,
        strict: bool = True,
        max_swings: int = 100,
    ) -> None:

        if lookback < 1:

            raise ValueError(
                "lookback must be >= 1."
            )

        if min_distance < 1:

            raise ValueError(
                "min_distance must be >= 1."
            )

        if min_price_distance < 0:

            raise ValueError(
                "min_price_distance cannot be negative."
            )

        if max_swings < 1:

            raise ValueError(
                "max_swings must be >= 1."
            )

        self.config = SwingConfig(
            lookback=lookback,
            min_distance=min_distance,
            min_price_distance=min_price_distance,
            strict=strict,
            max_swings=max_swings,
        )

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def detect(
        self,
        candles: list[MarketCandle],
    ) -> list[SwingPoint]:
        """
        Detect confirmed structural swings.

        Returns chronologically ordered SwingPoint objects.
        """

        self._validate_candles(candles)

        required = max(
            self.config.lookback * 2 + 1,
            MIN_SWING_CANDLES,
        )

        if len(candles) < required:

            return []

        candidates: list[SwingPoint] = []

        start = self.config.lookback

        end = (
            len(candles)
            - self.config.lookback
        )

        for index in range(
            start,
            end,
        ):

            candle = candles[index]

            if self._is_swing_high(
                candles,
                index,
            ):

                candidates.append(
                    SwingPoint(
                        index=index,
                        price=float(candle.high),
                        timestamp=candle.timestamp,
                        swing_type=SwingType.HIGH,
                    )
                )

            if self._is_swing_low(
                candles,
                index,
            ):

                candidates.append(
                    SwingPoint(
                        index=index,
                        price=float(candle.low),
                        timestamp=candle.timestamp,
                        swing_type=SwingType.LOW,
                    )
                )

        filtered = self._filter_candidates(
            candidates
        )

        return filtered[
            -self.config.max_swings:
        ]

    # =========================================================================
    # VALIDATION
    # =========================================================================

    @staticmethod
    def _validate_candles(
        candles: list[MarketCandle],
    ) -> None:
        """
        Validate candle integrity.
        """

        if candles is None:

            raise ValueError(
                "candles cannot be None."
            )

        if not isinstance(
            candles,
            list,
        ):

            raise ValueError(
                "candles must be a list."
            )

        previous_timestamp = None

        for index, candle in enumerate(
            candles
        ):

            if candle is None:

                raise ValueError(
                    f"candle[{index}] cannot be None."
                )

            try:

                open_price = float(
                    candle.open
                )

                high_price = float(
                    candle.high
                )

                low_price = float(
                    candle.low
                )

                close_price = float(
                    candle.close
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    f"candle[{index}] contains "
                    "non-numeric OHLC values."
                ) from exc

            if high_price < low_price:

                raise ValueError(
                    f"candle[{index}] has high < low."
                )

            if not (
                low_price
                <= open_price
                <= high_price
            ):

                raise ValueError(
                    f"candle[{index}] open is "
                    "outside candle range."
                )

            if not (
                low_price
                <= close_price
                <= high_price
            ):

                raise ValueError(
                    f"candle[{index}] close is "
                    "outside candle range."
                )

            if candle.timestamp is None:

                raise ValueError(
                    f"candle[{index}] timestamp "
                    "cannot be None."
                )

            if (
                previous_timestamp is not None
                and candle.timestamp
                <= previous_timestamp
            ):

                raise ValueError(
                    "candles must be strictly "
                    "chronological."
                )

            previous_timestamp = (
                candle.timestamp
            )

    # =========================================================================
    # SWING HIGH
    # =========================================================================

    def _is_swing_high(
        self,
        candles: list[MarketCandle],
        index: int,
    ) -> bool:
        """
        Determine whether a candle is a confirmed swing high.
        """

        current = candles[index]

        start = (
            index
            - self.config.lookback
        )

        end = (
            index
            + self.config.lookback
        )

        for neighbour_index in range(
            start,
            end + 1,
        ):

            if neighbour_index == index:

                continue

            neighbour = candles[
                neighbour_index
            ]

            if self.config.strict:

                if (
                    neighbour.high
                    >= current.high
                ):

                    return False

            elif (
                neighbour.high
                > current.high
            ):

                return False

        return True

    # =========================================================================
    # SWING LOW
    # =========================================================================

    def _is_swing_low(
        self,
        candles: list[MarketCandle],
        index: int,
    ) -> bool:
        """
        Determine whether a candle is a confirmed swing low.
        """

        current = candles[index]

        start = (
            index
            - self.config.lookback
        )

        end = (
            index
            + self.config.lookback
        )

        for neighbour_index in range(
            start,
            end + 1,
        ):

            if neighbour_index == index:

                continue

            neighbour = candles[
                neighbour_index
            ]

            if self.config.strict:

                if (
                    neighbour.low
                    <= current.low
                ):

                    return False

            elif (
                neighbour.low
                < current.low
            ):

                return False

        return True

    # =========================================================================
    # CANDIDATE FILTERING
    # =========================================================================

    def _filter_candidates(
        self,
        candidates: list[SwingPoint],
    ) -> list[SwingPoint]:
        """
        Remove redundant same-type swings.

        When two same-type swings compete inside the minimum distance,
        the more structurally extreme point wins:

            HIGH -> higher price
            LOW  -> lower price
        """

        if not candidates:

            return []

        candidates = sorted(
            candidates,
            key=lambda swing: (
                swing.index,
                0
                if swing.swing_type
                == SwingType.HIGH
                else 1,
            ),
        )

        accepted: list[SwingPoint] = []

        last_by_type: dict[
            SwingType,
            SwingPoint | None,
        ] = {
            SwingType.HIGH: None,
            SwingType.LOW: None,
        }

        for candidate in candidates:

            previous = last_by_type[
                candidate.swing_type
            ]

            if previous is None:

                accepted.append(
                    candidate
                )

                last_by_type[
                    candidate.swing_type
                ] = candidate

                continue

            distance = (
                candidate.index
                - previous.index
            )

            if (
                distance
                < self.config.min_distance
            ):

                stronger = (
                    self._more_extreme(
                        previous,
                        candidate,
                    )
                )

                if stronger is previous:

                    continue

                try:

                    accepted.remove(
                        previous
                    )

                except ValueError:

                    pass

                accepted.append(
                    candidate
                )

                last_by_type[
                    candidate.swing_type
                ] = candidate

                continue

            if (
                self.config.min_price_distance
                > 0
            ):

                price_distance = abs(
                    candidate.price
                    - previous.price
                )

                if (
                    price_distance
                    < self.config.min_price_distance
                ):

                    continue

            accepted.append(
                candidate
            )

            last_by_type[
                candidate.swing_type
            ] = candidate

        accepted.sort(
            key=lambda swing: (
                swing.index,
                0
                if swing.swing_type
                == SwingType.HIGH
                else 1,
            )
        )

        return accepted

    # =========================================================================
    # EXTREME RESOLUTION
    # =========================================================================

    @staticmethod
    def _more_extreme(
        first: SwingPoint,
        second: SwingPoint,
    ) -> SwingPoint:
        """
        Return the more structurally extreme swing.
        """

        if (
            first.swing_type
            != second.swing_type
        ):

            return first

        if (
            first.swing_type
            == SwingType.HIGH
        ):

            return (
                first
                if first.price >= second.price
                else second
            )

        return (
            first
            if first.price <= second.price
            else second
        )
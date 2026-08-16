"""
===============================================================================
COSMOS Dow Theory Engine

Production-grade Dow Theory market-structure classification.

Converts confirmed swing points into:

    Higher High  (HH)
    Higher Low   (HL)
    Lower High   (LH)
    Lower Low    (LL)

Design goals
------------
- Preserve the existing ``list[StructureType]`` public API.
- Compare HIGHs only against previous HIGHs.
- Compare LOWs only against previous LOWs.
- Preserve chronological structural ordering.
- Ignore malformed / unsupported swing objects safely.
- Handle equal-price swings deterministically.
- Avoid mutating caller-owned swing data.
- Provide reusable structural helpers for future chart-lock /
  analysis-artifact integration.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ai.models import SwingPoint
from ai.models import SwingType

from ai.agents.trend.models import StructureType


# =============================================================================
# INTERNAL CLASSIFICATION
# =============================================================================


class _Comparison(str, Enum):
    HIGHER = "HIGHER"
    LOWER = "LOWER"
    EQUAL = "EQUAL"


# =============================================================================
# STRUCTURE EVENT
# =============================================================================


@dataclass(frozen=True, slots=True)
class _StructureEvent:
    """
    Internal structural classification.

    This model is intentionally private for now.

    The public API continues to return ``StructureType`` so existing
    downstream agents remain compatible.
    """

    index: int
    price: float
    swing_type: SwingType
    structure: StructureType


# =============================================================================
# ENGINE
# =============================================================================


class DowEngine:
    """
    Production-grade Dow Theory structure engine.

    The engine maintains two independent structural streams:

        HIGH stream:
            HIGH → HIGH → HIGH
            ↓
            HH / LH

        LOW stream:
            LOW → LOW → LOW
            ↓
            HL / LL

    The resulting classifications are then merged chronologically.

    This is important because a HIGH must never be compared directly
    against a LOW.
    """

    AGENT_NAME = "dow_structure"
    ENGINE_VERSION = "2.0.0"

    def analyze(
        self,
        swings: list[SwingPoint],
    ) -> list[StructureType]:
        """
        Convert swing points into chronological Dow structure.

        Parameters
        ----------
        swings:
            Confirmed SwingPoint objects.

        Returns
        -------
        list[StructureType]
            Chronologically ordered structural classifications.

        Examples
        --------
        HIGH 100
        HIGH 110
        LOW   95
        LOW  105

        becomes:

            HH
            HL
        """

        events = self._classify(
            swings
        )

        return [
            event.structure
            for event in events
        ]

    # =========================================================================
    # INTERNAL CLASSIFICATION
    # =========================================================================

    def _classify(
        self,
        swings: list[SwingPoint],
    ) -> list[_StructureEvent]:
        """
        Perform complete structural classification.
        """

        if not swings:
            return []

        ordered = self._normalize_swings(
            swings
        )

        previous_high: SwingPoint | None = None
        previous_low: SwingPoint | None = None

        events: list[_StructureEvent] = []

        for swing in ordered:

            if swing.swing_type == SwingType.HIGH:

                if previous_high is None:

                    previous_high = swing

                    continue

                comparison = self._compare(
                    swing.price,
                    previous_high.price,
                )

                structure = (
                    self._classify_high(
                        comparison
                    )
                )

                events.append(
                    _StructureEvent(
                        index=swing.index,
                        price=swing.price,
                        swing_type=SwingType.HIGH,
                        structure=structure,
                    )
                )

                previous_high = swing

            elif swing.swing_type == SwingType.LOW:

                if previous_low is None:

                    previous_low = swing

                    continue

                comparison = self._compare(
                    swing.price,
                    previous_low.price,
                )

                structure = (
                    self._classify_low(
                        comparison
                    )
                )

                events.append(
                    _StructureEvent(
                        index=swing.index,
                        price=swing.price,
                        swing_type=SwingType.LOW,
                        structure=structure,
                    )
                )

                previous_low = swing

        return events

    # =========================================================================
    # NORMALIZATION
    # =========================================================================

    @staticmethod
    def _normalize_swings(
        swings: list[SwingPoint],
    ) -> list[SwingPoint]:
        """
        Return a deterministic chronological swing sequence.

        The original list is never mutated.
        """

        valid: list[SwingPoint] = []

        for swing in swings:

            if not isinstance(
                swing,
                SwingPoint,
            ):
                continue

            if swing.swing_type not in (
                SwingType.HIGH,
                SwingType.LOW,
            ):
                continue

            valid.append(swing)

        return sorted(
            valid,
            key=lambda item: (
                item.index,
                item.timestamp,
            ),
        )

    # =========================================================================
    # COMPARISON
    # =========================================================================

    @staticmethod
    def _compare(
        current: float,
        previous: float,
    ) -> _Comparison:
        """
        Compare two swing prices.
        """

        if current > previous:
            return _Comparison.HIGHER

        if current < previous:
            return _Comparison.LOWER

        return _Comparison.EQUAL

    # =========================================================================
    # HIGH CLASSIFICATION
    # =========================================================================

    @staticmethod
    def _classify_high(
        comparison: _Comparison,
    ) -> StructureType:
        """
        Classify a HIGH relative to the previous HIGH.

        Equal highs are treated as LH rather than HH.

        Equal highs represent an important liquidity condition and
        should not be interpreted as a new higher high.
        """

        if comparison == _Comparison.HIGHER:
            return StructureType.HH

        return StructureType.LH

    # =========================================================================
    # LOW CLASSIFICATION
    # =========================================================================

    @staticmethod
    def _classify_low(
        comparison: _Comparison,
    ) -> StructureType:
        """
        Classify a LOW relative to the previous LOW.

        Equal lows are treated as LL rather than HL.

        Equal lows represent an important liquidity condition and
        should not be interpreted as a new higher low.
        """

        if comparison == _Comparison.HIGHER:
            return StructureType.HL

        return StructureType.LL

    # =========================================================================
    # EXTENDED STRUCTURE ACCESS
    # =========================================================================

    def classify_events(
        self,
        swings: list[SwingPoint],
    ) -> list[dict[str, object]]:
        """
        Return detailed structural events.

        This method does NOT replace ``analyze()``.

        It exists as a richer API for future systems such as:

            - chart overlays
            - analysis locking
            - structure annotations
            - BOS / CHOCH engines
            - audit/debug views

        Example output:

            {
                "index": 42,
                "price": 1.1050,
                "swing_type": "HIGH",
                "structure": "HIGHER_HIGH",
            }
        """

        events = self._classify(
            swings
        )

        return [
            {
                "index": event.index,
                "price": event.price,
                "swing_type": event.swing_type.value,
                "structure": event.structure.value,
            }
            for event in events
        ]
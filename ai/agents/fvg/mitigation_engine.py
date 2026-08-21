"""
===============================================================================
COSMOS Fair Value Gap Mitigation Engine V2

Production-grade lifecycle engine for tracking price interaction with
previously detected Fair Value Gaps.

Lifecycle:

    UNTOUCHED
        ↓
      TESTED
        ↓
     PARTIAL
        ↓
      FULL

The engine tracks:

    - first touch
    - repeated mitigation
    - maximum penetration
    - fill ratio
    - mitigation count
    - lifecycle status
    - mitigation evidence

Design goals:

    - Deterministic behavior
    - Stable existing API
    - Monotonic fill progression
    - Safe repeated analysis
    - No mutation of unrelated FVG properties
    - Bounded fill ratios
    - Explicit lifecycle evidence
    - Future-ready for CE, displacement, volume,
      session and multi-timeframe confluence

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

import math

from ai.agents.fvg.constants import (
    DEEP_FILL_RATIO,
    FULL_FILL_RATIO,
    MAX_FVG_COUNT,
    MAX_SCORE,
    PARTIAL_FILL_RATIO,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGMitigationResult,
    FVGStatus,
    MitigationStatus,
)

from ai.agents.fvg.utils import (
    apply_fill_to_fvg,
    calculate_fill_ratio,
    candle_touches_fvg,
)


class MitigationEngine:
    """
    Tracks the lifecycle of detected Fair Value Gaps.

    The engine treats mitigation as a monotonic process:

        fill_ratio[n] >= fill_ratio[n-1]

    A previously achieved fill depth is never reduced by a later candle.
    """

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        fvgs: list[FairValueGap],
        candles,
    ) -> list[FVGMitigationResult]:
        """
        Analyze price interaction with all supplied FVGs.

        Returns one FVGMitigationResult for each valid FVG.
        """

        results: list[FVGMitigationResult] = []

        if not fvgs or candles is None:
            return results

        try:
            candle_count = len(candles)
        except TypeError:
            return results

        if candle_count == 0:
            return results

        for fvg in fvgs[:MAX_FVG_COUNT]:
            result = self._analyze_fvg(
                fvg=fvg,
                candles=candles,
                candle_count=candle_count,
            )

            results.append(result)

        return results

    # =========================================================================
    # SINGLE FVG ANALYSIS
    # =========================================================================

    def _analyze_fvg(
        self,
        fvg: FairValueGap,
        candles,
        candle_count: int,
    ) -> FVGMitigationResult:
        """
        Analyze mitigation for one FVG.
        """

        evidence: list[str] = []

        previous_fill = self._normalize_ratio(
            fvg.fill_ratio
        )

        best_fill = previous_fill

        touch_count = 0

        start_index = (
            max(
                0,
                int(fvg.third_candle_index) + 1,
            )
        )

        # ---------------------------------------------------------------------
        # Ignore candles that existed before the FVG completed.
        # ---------------------------------------------------------------------

        if start_index < candle_count:

            for candle in candles[start_index:]:

                if not candle_touches_fvg(
                    candle,
                    fvg,
                ):
                    continue

                touch_count += 1

                fill_ratio = self._safe_fill_ratio(
                    candle,
                    fvg,
                )

                if fill_ratio > best_fill:
                    best_fill = fill_ratio

        # ---------------------------------------------------------------------
        # Determine whether this analysis produced a new touch.
        #
        # Existing mitigation_count is preserved so repeated engine calls do
        # not artificially erase lifecycle history.
        # ---------------------------------------------------------------------

        touched = touch_count > 0

        if touched:
            fvg.mitigation_count += touch_count

        # ---------------------------------------------------------------------
        # Apply the strongest observed fill.
        # ---------------------------------------------------------------------

        apply_fill_to_fvg(
            fvg,
            best_fill,
        )

        # ---------------------------------------------------------------------
        # Explicit lifecycle classification.
        # ---------------------------------------------------------------------

        self._apply_lifecycle_status(
            fvg=fvg,
            touched=touched,
            fill_ratio=best_fill,
        )

        # ---------------------------------------------------------------------
        # Build evidence.
        # ---------------------------------------------------------------------

        if not touched:

            evidence.append(
                "FVG Untouched"
            )

        else:

            evidence.append(
                "FVG Tested"
            )

            evidence.append(
                f"Mitigation Touches: {touch_count}"
            )

            evidence.append(
                f"Maximum Fill: {best_fill:.4f}"
            )

            if best_fill >= FULL_FILL_RATIO:

                evidence.append(
                    "FVG Fully Mitigated"
                )

            elif best_fill >= DEEP_FILL_RATIO:

                evidence.append(
                    "FVG Deeply Mitigated"
                )

            elif best_fill >= PARTIAL_FILL_RATIO:

                evidence.append(
                    "FVG Partially Mitigated"
                )

            else:

                evidence.append(
                    "FVG Lightly Tested"
                )

        # ---------------------------------------------------------------------
        # Preserve lifecycle evidence without duplicating identical entries.
        # ---------------------------------------------------------------------

        self._append_unique_evidence(
            fvg,
            evidence,
        )

        # ---------------------------------------------------------------------
        # Final result.
        # ---------------------------------------------------------------------

        return FVGMitigationResult(
            fvg=fvg,

            status=fvg.mitigation_status,

            fill_ratio=round(
                self._normalize_ratio(
                    fvg.fill_ratio
                ),
                4,
            ),

            touched=touched,

            partially_filled=(
                fvg.mitigation_status
                == MitigationStatus.PARTIAL
            ),

            fully_filled=(
                fvg.mitigation_status
                == MitigationStatus.FULL
            ),

            invalidated=(
                fvg.mitigation_status
                == MitigationStatus.INVALIDATED
            ),

            evidence=evidence,
        )

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    @staticmethod
    def _apply_lifecycle_status(
        fvg: FairValueGap,
        touched: bool,
        fill_ratio: float,
    ) -> None:
        """
        Synchronize FVG status with mitigation lifecycle.

        Existing invalidation is preserved.
        """

        if not fvg.valid:

            fvg.status = FVGStatus.INVALID

            fvg.mitigation_status = (
                MitigationStatus.INVALIDATED
            )

            return

        if fill_ratio >= FULL_FILL_RATIO:

            fvg.status = FVGStatus.FILLED

            fvg.mitigation_status = (
                MitigationStatus.FULL
            )

            return

        if fill_ratio >= PARTIAL_FILL_RATIO:

            fvg.status = FVGStatus.PARTIAL

            fvg.mitigation_status = (
                MitigationStatus.PARTIAL
            )

            return

        if touched:

            fvg.status = FVGStatus.TESTED

            fvg.mitigation_status = (
                MitigationStatus.UNTOUCHED
            )

            return

        fvg.status = FVGStatus.FRESH

        fvg.mitigation_status = (
            MitigationStatus.UNTOUCHED
        )

    # =========================================================================
    # SAFE CALCULATIONS
    # =========================================================================

    @staticmethod
    def _safe_fill_ratio(
        candle,
        fvg: FairValueGap,
    ) -> float:
        """
        Safely calculate a bounded fill ratio.
        """

        try:
            ratio = float(
                calculate_fill_ratio(
                    candle,
                    fvg,
                )
            )
        except (
            TypeError,
            ValueError,
            AttributeError,
            ZeroDivisionError,
        ):
            return 0.0

        return MitigationEngine._normalize_ratio(
            ratio
        )

    @staticmethod
    def _normalize_ratio(
        value: float,
    ) -> float:
        """
        Clamp a fill ratio to the valid 0-1 interval.
        """

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        if not math.isfinite(value):
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                value,
            ),
        )

    # =========================================================================
    # EVIDENCE
    # =========================================================================

    @staticmethod
    def _append_unique_evidence(
        fvg: FairValueGap,
        evidence: list[str],
    ) -> None:
        """
        Append evidence while preventing exact duplicates.
        """

        for item in evidence:

            if item not in fvg.evidence:

                fvg.evidence.append(
                    item
                )
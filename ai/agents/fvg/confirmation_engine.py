"""
===============================================================================
COSMOS Fair Value Gap Confirmation Engine V2

Evaluates whether detected Fair Value Gaps contain enough finalized structural
evidence to be considered actionable.

Pipeline position:

    Detection
        ↓
    Mitigation
        ↓
    Inversion
        ↓
    Probability
        ↓
    Confidence
        ↓
    Confirmation  ← this engine
        ↓
    Mapping
        ↓
    Ranking
        ↓
    Final Analysis

Design goals
------------
- Deterministic confirmation.
- Bounded confirmation score.
- Uses finalized upstream probability/confidence.
- Respects mitigation lifecycle.
- Respects invalidation.
- Respects directional validity.
- Handles inverted FVGs safely.
- Avoids duplicate evidence.
- Keeps the existing public API stable.
- Future-ready for BOS, CHOCH, sweep, OB, trend, volume, session and HTF
  confluence.

Important
---------
Confirmation is NOT a trade signal and is NOT a statistically validated
probability of winning.

It means that the FVG currently satisfies enough structural requirements to
remain actionable inside the FVG Agent.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.fvg.constants import (
    MIN_CONFIRMATION_CONFIDENCE,
    MIN_CONFIRMATION_PROBABILITY,
    MIN_CONFIRMATION_SCORE,
    MIN_CONFIRMATION_STRENGTH,
    STRONG_CONFIRMATION_CONFIDENCE,
    STRONG_CONFIRMATION_PROBABILITY,
    STRONG_CONFIRMATION_SCORE,
    STRONG_CONFIRMATION_STRENGTH,
)

from ai.agents.fvg.models import (
    FairValueGap,
    FVGConfirmation,
    FVGDirection,
    FVGStatus,
    InversionStatus,
    MitigationStatus,
)


class ConfirmationEngine:
    """
    Determines whether an FVG has sufficient finalized evidence.

    Confirmation consists of five primary structural checks:

        1. validity
        2. lifecycle / activity
        3. confidence
        4. probability
        5. strength

    Direction is additionally required for an actionable confirmation.

    A confirmed FVG therefore represents a structurally supported zone rather
    than merely a detected three-candle imbalance.
    """

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        fvgs: list[FairValueGap],
    ) -> list[FVGConfirmation]:
        """
        Confirm all supplied FVGs.

        Returns one FVGConfirmation for every input FVG.

        The method does not remove or reorder FVGs.
        """

        if not fvgs:
            return []

        confirmations: list[FVGConfirmation] = []

        for fvg in fvgs:
            confirmations.append(
                self._confirm(
                    fvg,
                )
            )

        return confirmations

    # =========================================================================
    # SINGLE FVG CONFIRMATION
    # =========================================================================

    def _confirm(
        self,
        fvg: FairValueGap,
    ) -> FVGConfirmation:
        """
        Evaluate one FVG.
        """

        reasons: list[str] = []

        # ---------------------------------------------------------------------
        # Hard validity gate.
        # ---------------------------------------------------------------------

        if not bool(
            getattr(
                fvg,
                "valid",
                False,
            )
        ):
            return self._result(
                fvg=fvg,
                score=0.0,
                confirmed=False,
                reasons=[
                    "FVG Invalid",
                ],
            )

        score = 0

        # ---------------------------------------------------------------------
        # 1. VALIDITY
        # ---------------------------------------------------------------------

        score += 1

        reasons.append(
            "FVG Valid",
        )

        # ---------------------------------------------------------------------
        # 2. LIFECYCLE / ACTIVE STATE
        # ---------------------------------------------------------------------

        lifecycle_passed = self._check_lifecycle(
            fvg,
            reasons,
        )

        if lifecycle_passed:
            score += 1

        # ---------------------------------------------------------------------
        # 3. CONFIDENCE
        # ---------------------------------------------------------------------

        confidence = self._safe_score(
            getattr(
                fvg,
                "confidence",
                0.0,
            )
        )

        if confidence >= (
            MIN_CONFIRMATION_CONFIDENCE
        ):
            score += 1

            reasons.append(
                "Meaningful Confidence",
            )

        if confidence >= (
            STRONG_CONFIRMATION_CONFIDENCE
        ):
            reasons.append(
                "High Confidence",
            )

        # ---------------------------------------------------------------------
        # 4. PROBABILITY
        # ---------------------------------------------------------------------

        probability = self._safe_score(
            getattr(
                fvg,
                "probability",
                0.0,
            )
        )

        if probability >= (
            MIN_CONFIRMATION_PROBABILITY
        ):
            score += 1

            reasons.append(
                "Meaningful Probability",
            )

        if probability >= (
            STRONG_CONFIRMATION_PROBABILITY
        ):
            reasons.append(
                "High Probability",
            )

        # ---------------------------------------------------------------------
        # 5. STRENGTH
        # ---------------------------------------------------------------------

        strength = self._safe_score(
            getattr(
                fvg,
                "strength",
                0.0,
            )
        )

        if strength >= (
            MIN_CONFIRMATION_STRENGTH
        ):
            score += 1

            reasons.append(
                "Meaningful FVG Strength",
            )

        if strength >= (
            STRONG_CONFIRMATION_STRENGTH
        ):
            reasons.append(
                "Strong FVG",
            )

        # ---------------------------------------------------------------------
        # DIRECTION
        #
        # Direction is not counted as an additional point because the
        # confirmation score remains a five-factor contract.
        # It is instead an actionable gate.
        # ---------------------------------------------------------------------

        directional = self._check_direction(
            fvg,
            reasons,
        )

        # ---------------------------------------------------------------------
        # INVERSION
        #
        # A confirmed inversion can remain useful as an IFVG, but the current
        # direction must still be valid. We therefore do not automatically
        # reject it.
        # ---------------------------------------------------------------------

        self._add_inversion_context(
            fvg,
            reasons,
        )

        # ---------------------------------------------------------------------
        # FINAL DECISION
        # ---------------------------------------------------------------------

        confirmed = (
            score >= MIN_CONFIRMATION_SCORE
            and
            lifecycle_passed
            and
            directional
            and
            fvg.status != FVGStatus.FILLED
            and
            fvg.status != FVGStatus.INVALID
            and
            fvg.mitigation_status
            != MitigationStatus.FULL
            and
            fvg.mitigation_status
            != MitigationStatus.INVALIDATED
        )

        # ---------------------------------------------------------------------
        # Confirmation classification.
        # ---------------------------------------------------------------------

        if (
            confirmed
            and
            score >= STRONG_CONFIRMATION_SCORE
            and
            confidence >= STRONG_CONFIRMATION_CONFIDENCE
            and
            probability >= STRONG_CONFIRMATION_PROBABILITY
            and
            strength >= STRONG_CONFIRMATION_STRENGTH
        ):
            reasons.append(
                "Strong Confirmation",
            )

        elif confirmed:
            reasons.append(
                "FVG Confirmed",
            )

        else:
            reasons.append(
                "Insufficient Confirmation",
            )

        # ---------------------------------------------------------------------
        # Attach only one confirmation evidence marker.
        # ---------------------------------------------------------------------

        self._update_fvg_evidence(
            fvg,
            confirmed,
        )

        return self._result(
            fvg=fvg,
            score=float(score),
            confirmed=confirmed,
            reasons=reasons,
        )

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    @staticmethod
    def _check_lifecycle(
        fvg: FairValueGap,
        reasons: list[str],
    ) -> bool:
        """
        Determine whether the FVG remains active enough for confirmation.

        Fresh and partially mitigated FVGs are actionable.

        Tested FVGs are allowed if they have not become fully mitigated.

        Filled and invalid zones fail the lifecycle gate.
        """

        status = getattr(
            fvg,
            "status",
            FVGStatus.INVALID,
        )

        mitigation = getattr(
            fvg,
            "mitigation_status",
            MitigationStatus.UNTOUCHED,
        )

        if status == FVGStatus.FRESH:

            reasons.append(
                "Fresh FVG",
            )

            return (
                mitigation
                != MitigationStatus.FULL
                and
                mitigation
                != MitigationStatus.INVALIDATED
            )

        if status == FVGStatus.PARTIAL:

            reasons.append(
                "Partially Mitigated FVG",
            )

            return (
                mitigation
                != MitigationStatus.FULL
                and
                mitigation
                != MitigationStatus.INVALIDATED
            )

        if status == FVGStatus.TESTED:

            reasons.append(
                "Tested FVG",
            )

            return (
                mitigation
                != MitigationStatus.FULL
                and
                mitigation
                != MitigationStatus.INVALIDATED
            )

        if status == FVGStatus.FILLED:

            reasons.append(
                "FVG Fully Filled",
            )

            return False

        if status == FVGStatus.INVALID:

            reasons.append(
                "FVG Invalidated",
            )

            return False

        reasons.append(
            "Unknown FVG Lifecycle",
        )

        return False

    # =========================================================================
    # DIRECTION
    # =========================================================================

    @staticmethod
    def _check_direction(
        fvg: FairValueGap,
        reasons: list[str],
    ) -> bool:
        """
        Verify that the FVG has an actionable direction.
        """

        direction = getattr(
            fvg,
            "direction",
            FVGDirection.NEUTRAL,
        )

        if direction == FVGDirection.BULLISH:

            reasons.append(
                "BULLISH Direction",
            )

            return True

        if direction == FVGDirection.BEARISH:

            reasons.append(
                "BEARISH Direction",
            )

            return True

        reasons.append(
            "Neutral Direction",
        )

        return False

    # =========================================================================
    # INVERSION
    # =========================================================================

    @staticmethod
    def _add_inversion_context(
        fvg: FairValueGap,
        reasons: list[str],
    ) -> None:
        """
        Add inversion context without automatically rejecting IFVGs.
        """

        inversion_status = getattr(
            fvg,
            "inversion_status",
            InversionStatus.NONE,
        )

        if inversion_status == (
            InversionStatus.CONFIRMED
        ):

            reasons.append(
                "Confirmed IFVG",
            )

        elif inversion_status == (
            InversionStatus.POTENTIAL
        ):

            reasons.append(
                "Potential FVG Inversion",
            )

    # =========================================================================
    # NUMERIC SAFETY
    # =========================================================================

    @staticmethod
    def _safe_score(
        value,
    ) -> float:
        """
        Convert arbitrary score input into bounded 0-100 form.
        """

        try:
            score = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        if score != score:
            return 0.0

        if score == float("inf"):
            return 100.0

        if score == float("-inf"):
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

    # =========================================================================
    # EVIDENCE
    # =========================================================================

    @staticmethod
    def _update_fvg_evidence(
        fvg: FairValueGap,
        confirmed: bool,
    ) -> None:
        """
        Add confirmation evidence exactly once.

        This makes repeated execution idempotent with respect to evidence.
        """

        existing = list(
            getattr(
                fvg,
                "evidence",
                [],
            )
        )

        confirmation_labels = {
            "FVG Confirmed",
            "Strong Confirmation",
            "Insufficient Confirmation",
        }

        existing = [
            item
            for item in existing
            if str(item).strip()
            not in confirmation_labels
        ]

        if confirmed:
            existing.append(
                "FVG Confirmed",
            )

        fvg.evidence = existing

    # =========================================================================
    # RESULT
    # =========================================================================

    @staticmethod
    def _result(
        *,
        fvg: FairValueGap,
        score: float,
        confirmed: bool,
        reasons: list[str],
    ) -> FVGConfirmation:
        """
        Build a stable FVGConfirmation object.
        """

        return FVGConfirmation(
            fvg=fvg,
            confirmed=confirmed,
            score=float(score),
            reasons=reasons,
        )

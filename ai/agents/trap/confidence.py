"""
===============================================================================
COSMOS Trap Agent Confidence Engine

Calculates confidence in a detected trap from independent evidence.

Important:
    Confidence is an evidence-quality score.
    It is NOT a guaranteed probability of profit.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.trap.constants import (
    CONFLICT_PENALTY,
    HIGH_TRAP_CONFIDENCE,
    VERY_HIGH_TRAP_CONFIDENCE,
)

from ai.agents.trap.models import (
    BreakoutEvent,
    ReclaimEvent,
    RejectionEvent,
    TrapCandidate,
    TrapDirection,
    TrapProbability,
    TrapResult,
    TrapType,
    TrapVolumeEvidence,
    FollowThroughFailure,
)

from ai.agents.trap.utils import normalize_score


class TrapConfidenceEngine:
    """
    Calculates confidence for COSMOS trap detections.

    Evidence layers:

        Breakout
        Reclaim
        Rejection
        Volume/activity
        Follow-through failure
        Directional agreement
        Evidence consistency
    """

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        candidate: TrapCandidate,
        probability: TrapProbability | None = None,
    ) -> float:
        """
        Calculate final confidence from a TrapCandidate.

        Returns:
            Confidence score from 0 to 100.
        """

        if candidate is None:

            return 0.0

        score = 0.0

        evidence_count = 0

        # ---------------------------------------------------------------------
        # Breakout
        # ---------------------------------------------------------------------

        if self._has_breakout(
            candidate.breakout
        ):

            score += 15.0
            evidence_count += 1

        # ---------------------------------------------------------------------
        # Reclaim
        # ---------------------------------------------------------------------

        if self._has_reclaim(
            candidate.reclaim
        ):

            score += 25.0
            evidence_count += 1

        # ---------------------------------------------------------------------
        # Rejection
        # ---------------------------------------------------------------------

        if self._has_rejection(
            candidate.rejection
        ):

            rejection_strength = (
                normalize_score(
                    candidate.rejection.strength
                )
            )

            score += (
                15.0
                +
                rejection_strength
                * 0.10
            )

            evidence_count += 1

        # ---------------------------------------------------------------------
        # Volume
        # ---------------------------------------------------------------------

        if self._has_volume(
            candidate.volume
        ):

            volume_strength = (
                normalize_score(
                    candidate.volume.strength
                )
            )

            score += (
                5.0
                +
                volume_strength
                * 0.10
            )

            evidence_count += 1

        # ---------------------------------------------------------------------
        # Follow-through failure
        # ---------------------------------------------------------------------

        if self._has_follow_through(
            candidate.follow_through
        ):

            failure_strength = (
                normalize_score(
                    candidate
                    .follow_through
                    .failure_strength
                )
            )

            score += (
                10.0
                +
                failure_strength
                * 0.10
            )

            evidence_count += 1

        # ---------------------------------------------------------------------
        # Candidate directional consistency
        # ---------------------------------------------------------------------

        if self._direction_is_consistent(
            candidate
        ):

            score += 10.0

        else:

            score -= CONFLICT_PENALTY

        # ---------------------------------------------------------------------
        # Probability agreement
        # ---------------------------------------------------------------------

        if probability is not None:

            probability_score = (
                self._probability_confidence(
                    probability
                )
            )

            score += (
                probability_score
                * 0.10
            )

        # ---------------------------------------------------------------------
        # Evidence completeness
        # ---------------------------------------------------------------------

        if evidence_count >= 4:

            score += 5.0

        elif evidence_count >= 3:

            score += 3.0

        # ---------------------------------------------------------------------
        # Trap type requirement
        # ---------------------------------------------------------------------

        if (
            candidate.trap_type
            ==
            TrapType.NONE
        ):

            score = min(
                score,
                40.0,
            )

        # ---------------------------------------------------------------------
        # Final normalization
        # ---------------------------------------------------------------------

        return round(
            normalize_score(
                score
            ),
            2,
        )

    # =========================================================================
    # RESULT ANALYSIS
    # =========================================================================

    def build_result(
        self,
        candidate: TrapCandidate,
        probability: TrapProbability | None = None,
    ) -> TrapResult:
        """
        Build the final TrapResult.

        This method combines:

            candidate
            probability
            confidence
        """

        if candidate is None:

            return TrapResult()

        confidence = self.analyze(
            candidate,
            probability,
        )

        # ---------------------------------------------------------------------
        # Directional probability
        # ---------------------------------------------------------------------

        directional_probability = 50.0

        if probability is not None:

            if (
                probability.direction
                ==
                TrapDirection.BULLISH
            ):

                directional_probability = (
                    probability
                    .bullish_probability
                )

            elif (
                probability.direction
                ==
                TrapDirection.BEARISH
            ):

                directional_probability = (
                    probability
                    .bearish_probability
                )

            else:

                directional_probability = (
                    probability
                    .neutral_probability
                )

        # ---------------------------------------------------------------------
        # Validity
        # ---------------------------------------------------------------------

        valid = (
            candidate.detected
            and
            candidate.trap_type
            !=
            TrapType.NONE
            and
            confidence
            >=
            HIGH_TRAP_CONFIDENCE
        )

        # ---------------------------------------------------------------------
        # Evidence
        # ---------------------------------------------------------------------

        evidence = list(
            candidate.evidence
        )

        if probability is not None:

            evidence.extend(
                probability.evidence
            )

        evidence.append(
            f"Trap confidence: {confidence:.2f}"
        )

        if (
            confidence
            >=
            VERY_HIGH_TRAP_CONFIDENCE
        ):

            evidence.append(
                "Very high evidence confidence"
            )

        elif (
            confidence
            >=
            HIGH_TRAP_CONFIDENCE
        ):

            evidence.append(
                "High evidence confidence"
            )

        else:

            evidence.append(
                "Confidence below confirmation threshold"
            )

        return TrapResult(

            detected=(
                candidate.detected
            ),

            trap_type=(
                candidate.trap_type
            ),

            direction=(
                candidate.direction
            ),

            state=(
                candidate.state
            ),

            level=(
                candidate.level
            ),

            probability=round(
                directional_probability,
                2,
            ),

            confidence=round(
                confidence,
                2,
            ),

            score=round(
                candidate.score,
                2,
            ),

            valid=valid,

            evidence=evidence,

            breakout=(
                candidate.breakout
            ),

            reclaim=(
                candidate.reclaim
            ),

            rejection=(
                candidate.rejection
            ),

            volume=(
                candidate.volume
            ),

            follow_through=(
                candidate.follow_through
            ),

            probability_analysis=(
                probability
            ),

            metadata={
                "confirmation_threshold": (
                    HIGH_TRAP_CONFIDENCE
                ),
                "very_high_threshold": (
                    VERY_HIGH_TRAP_CONFIDENCE
                ),
            },
        )

    # =========================================================================
    # INDIVIDUAL EVIDENCE CHECKS
    # =========================================================================

    @staticmethod
    def _has_breakout(
        breakout: BreakoutEvent | None,
    ) -> bool:

        return (
            breakout is not None
            and
            breakout.detected
        )

    @staticmethod
    def _has_reclaim(
        reclaim: ReclaimEvent | None,
    ) -> bool:

        return (
            reclaim is not None
            and
            reclaim.detected
        )

    @staticmethod
    def _has_rejection(
        rejection: RejectionEvent | None,
    ) -> bool:

        return (
            rejection is not None
            and
            rejection.detected
        )

    @staticmethod
    def _has_volume(
        volume: TrapVolumeEvidence | None,
    ) -> bool:

        return (
            volume is not None
            and
            volume.available
        )

    @staticmethod
    def _has_follow_through(
        failure: FollowThroughFailure | None,
    ) -> bool:

        return (
            failure is not None
            and
            failure.detected
        )

    # =========================================================================
    # DIRECTION CONSISTENCY
    # =========================================================================

    @staticmethod
    def _direction_is_consistent(
        candidate: TrapCandidate,
    ) -> bool:
        """
        Verify that the major evidence components point in the same
        structural direction.
        """

        if candidate is None:

            return False

        expected_direction = (
            candidate.direction
        )

        if (
            expected_direction
            ==
            TrapDirection.NEUTRAL
        ):

            return False

        # ---------------------------------------------------------------------
        # Breakout direction
        # ---------------------------------------------------------------------

        if (
            candidate.breakout is not None
            and
            candidate.breakout.detected
        ):

            if (
                candidate.breakout.direction
                !=
                expected_direction
            ):

                return False

        # ---------------------------------------------------------------------
        # Reclaim direction
        # ---------------------------------------------------------------------

        if (
            candidate.reclaim is not None
            and
            candidate.reclaim.detected
        ):

            if (
                candidate.reclaim.direction
                !=
                expected_direction
            ):

                return False

        # ---------------------------------------------------------------------
        # Rejection direction
        # ---------------------------------------------------------------------

        if (
            candidate.rejection is not None
            and
            candidate.rejection.detected
        ):

            if (
                candidate.rejection.direction
                !=
                expected_direction
            ):

                return False

        return True

    # =========================================================================
    # PROBABILITY CONFIDENCE
    # =========================================================================

    @staticmethod
    def _probability_confidence(
        probability: TrapProbability,
    ) -> float:
        """
        Convert directional separation into a 0-100 confidence component.
        """

        if probability is None:

            return 0.0

        bullish = normalize_score(
            probability.bullish_probability
        )

        bearish = normalize_score(
            probability.bearish_probability
        )

        separation = abs(
            bullish
            -
            bearish
        )

        return normalize_score(
            separation
            * 2.0
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

trap_confidence_engine = TrapConfidenceEngine()
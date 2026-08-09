"""
===============================================================================
COSMOS Trap Confirmation Engine

Central integration layer for the COSMOS Trap Agent.

Pipeline:

    Validation
        ↓
    Breakout
        ↓
    Reclaim
        ↓
    Rejection
        ↓
    Volume
        ↓
    Follow-through
        ↓
    Candidate
        ↓
    Probability
        ↓
    Confidence
        ↓
    TrapResult

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from typing import Any

from ai.agents.trap.breakout import (
    BreakoutEngine,
)

from ai.agents.trap.confidence import (
    TrapConfidenceEngine,
)

from ai.agents.trap.constants import (
    HIGH_TRAP_CONFIDENCE,
    MIN_TRAP_SCORE,
)

from ai.agents.trap.follow_through import (
    FollowThroughEngine,
)

from ai.agents.trap.models import (
    BreakoutEvent,
    FollowThroughFailure,
    ReclaimEvent,
    RejectionEvent,
    TrapCandidate,
    TrapDirection,
    TrapProbability,
    TrapResult,
    TrapState,
    TrapType,
    TrapVolumeEvidence,
)

from ai.agents.trap.probability import (
    TrapProbabilityEngine,
)

from ai.agents.trap.reclaim import (
    ReclaimEngine,
)

from ai.agents.trap.rejection import (
    RejectionEngine,
)

from ai.agents.trap.validator import (
    TrapValidator,
)

from ai.agents.trap.volume import (
    TrapVolumeEngine,
)


class TrapEngine:
    """
    Main COSMOS Trap Agent.

    This class is the only integration point that the rest of COSMOS needs
    to call for trap analysis.
    """

    def __init__(
        self,
        validator: TrapValidator | None = None,
        breakout_engine: BreakoutEngine | None = None,
        reclaim_engine: ReclaimEngine | None = None,
        rejection_engine: RejectionEngine | None = None,
        volume_engine: TrapVolumeEngine | None = None,
        follow_through_engine: FollowThroughEngine | None = None,
        probability_engine: TrapProbabilityEngine | None = None,
        confidence_engine: TrapConfidenceEngine | None = None,
    ) -> None:

        self.validator = (
            validator
            or TrapValidator()
        )

        self.breakout_engine = (
            breakout_engine
            or BreakoutEngine()
        )

        self.reclaim_engine = (
            reclaim_engine
            or ReclaimEngine()
        )

        self.rejection_engine = (
            rejection_engine
            or RejectionEngine()
        )

        self.volume_engine = (
            volume_engine
            or TrapVolumeEngine()
        )

        self.follow_through_engine = (
            follow_through_engine
            or FollowThroughEngine()
        )

        self.probability_engine = (
            probability_engine
            or TrapProbabilityEngine()
        )

        self.confidence_engine = (
            confidence_engine
            or TrapConfidenceEngine()
        )

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def analyze(
        self,
        candles,
        resistance: float | None = None,
        support: float | None = None,
        lookback: int = 20,
    ) -> TrapResult:
        """
        Analyze the latest market candles for a possible trap.

        Returns one TrapResult representing the latest actionable trap
        candidate.
        """

        # ---------------------------------------------------------------------
        # Validation
        # ---------------------------------------------------------------------

        validation = self.validator.validate(
            candles,
            lookback=lookback,
        )

        if not validation.valid:

            return TrapResult(
                detected=False,
                trap_type=TrapType.NONE,
                direction=TrapDirection.NEUTRAL,
                state=TrapState.NONE,
                confidence=0.0,
                probability=0.0,
                score=0.0,
                valid=False,
                evidence=[
                    "Trap analysis validation failed"
                ],
                metadata={
                    "validation_errors": (
                        validation.errors
                    ),
                    "validation_warnings": (
                        validation.warnings
                    ),
                },
            )

        candle_list = list(
            candles
        )

        # ---------------------------------------------------------------------
        # Breakout
        # ---------------------------------------------------------------------

        breakout_events = (
            self.breakout_engine.detect(
                candle_list,
                resistance=resistance,
                support=support,
                lookback=lookback,
            )
        )

        if not breakout_events:

            return TrapResult(
                detected=False,
                trap_type=TrapType.NONE,
                direction=TrapDirection.NEUTRAL,
                state=TrapState.NONE,
                confidence=0.0,
                probability=0.0,
                score=0.0,
                valid=False,
                evidence=[
                    "No qualifying breakout detected"
                ],
                metadata={
                    "validation_warnings": (
                        validation.warnings
                    ),
                },
            )

        # ---------------------------------------------------------------------
        # Evaluate every detected breakout.
        # ---------------------------------------------------------------------

        candidates: list[
            TrapCandidate
        ] = []

        for breakout in breakout_events:

            candidate = self._build_candidate(
                candle_list,
                breakout,
                lookback,
            )

            if candidate is not None:

                candidates.append(
                    candidate
                )

        if not candidates:

            return TrapResult(
                detected=False,
                trap_type=TrapType.NONE,
                direction=TrapDirection.NEUTRAL,
                state=TrapState.NONE,
                confidence=0.0,
                probability=0.0,
                score=0.0,
                valid=False,
                evidence=[
                    "Breakout detected but no trap candidate formed"
                ],
            )

        # ---------------------------------------------------------------------
        # Select strongest candidate.
        # ---------------------------------------------------------------------

        candidate = max(
            candidates,
            key=lambda item: (
                float(
                    getattr(
                        item,
                        "score",
                        0.0,
                    )
                ),
                float(
                    getattr(
                        item,
                        "confidence",
                        0.0,
                    )
                ),
            ),
        )

        # ---------------------------------------------------------------------
        # Probability
        # ---------------------------------------------------------------------

        probability = (
            self.probability_engine.analyze(
                candidate
            )
        )

        # ---------------------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------------------

        result = (
            self.confidence_engine.build_result(
                candidate,
                probability,
            )
        )

        # ---------------------------------------------------------------------
        # Final engine metadata
        # ---------------------------------------------------------------------

        result.metadata.update(
            {
                "agent": "trap",
                "pipeline": [
                    "validation",
                    "breakout",
                    "reclaim",
                    "rejection",
                    "volume",
                    "follow_through",
                    "probability",
                    "confidence",
                ],
                "candidate_count": len(
                    candidates
                ),
                "validation_warnings": (
                    validation.warnings
                ),
            }
        )

        return result

    # =========================================================================
    # CANDIDATE BUILDER
    # =========================================================================

    def _build_candidate(
        self,
        candles,
        breakout: BreakoutEvent,
        lookback: int,
    ) -> TrapCandidate | None:
        """
        Build a TrapCandidate from all available evidence.
        """

        if (
            breakout is None
            or
            not breakout.detected
        ):

            return None

        # ---------------------------------------------------------------------
        # Reclaim
        # ---------------------------------------------------------------------

        reclaim = (
            self.reclaim_engine.analyze(
                candles,
                breakout,
            )
        )

        # ---------------------------------------------------------------------
        # Rejection
        # ---------------------------------------------------------------------

        rejection = (
            self.rejection_engine.analyze(
                candles[
                    breakout.candle_index
                ],
                breakout,
                reclaim,
            )
        )

        # ---------------------------------------------------------------------
        # Volume
        # ---------------------------------------------------------------------

        volume = (
            self.volume_engine.analyze(
                candles,
                breakout,
                reclaim,
                lookback=lookback,
            )
        )

        # ---------------------------------------------------------------------
        # Follow-through
        # ---------------------------------------------------------------------

        follow_through = (
            self.follow_through_engine.analyze(
                candles,
                breakout,
            )
        )

        # ---------------------------------------------------------------------
        # Trap classification
        # ---------------------------------------------------------------------

        trap_type = self._classify_trap(
            breakout,
            reclaim,
        )

        # ---------------------------------------------------------------------
        # Direction
        # ---------------------------------------------------------------------

        direction = (
            self._trap_direction(
                trap_type
            )
        )

        # ---------------------------------------------------------------------
        # State
        # ---------------------------------------------------------------------

        state = self._state(
            breakout,
            reclaim,
            rejection,
        )

        # ---------------------------------------------------------------------
        # Evidence
        # ---------------------------------------------------------------------

        evidence = []

        evidence.extend(
            breakout.evidence
        )

        evidence.extend(
            reclaim.evidence
        )

        evidence.extend(
            rejection.evidence
        )

        evidence.extend(
            volume.evidence
        )

        evidence.extend(
            follow_through.evidence
        )

        # ---------------------------------------------------------------------
        # Score
        # ---------------------------------------------------------------------

        score = self._score(
            breakout=breakout,
            reclaim=reclaim,
            rejection=rejection,
            volume=volume,
            follow_through=follow_through,
        )

        detected = (
            trap_type
            !=
            TrapType.NONE
        )

        # ---------------------------------------------------------------------
        # Candidate
        # ---------------------------------------------------------------------

        return TrapCandidate(

            detected=detected,

            trap_type=trap_type,

            direction=direction,

            state=state,

            level=float(
                breakout.level
            ),

            score=round(
                score,
                2,
            ),

            evidence=evidence,

            breakout=breakout,

            reclaim=reclaim,

            rejection=rejection,

            volume=volume,

            follow_through=follow_through,
        )

    # =========================================================================
    # CLASSIFICATION
    # =========================================================================

    @staticmethod
    def _classify_trap(
        breakout: BreakoutEvent,
        reclaim: ReclaimEvent,
    ) -> TrapType:
        """
        Classify breakout failure into bull trap or bear trap.

        Bullish breakout + reclaim below resistance:
            Bull trap.

        Bearish breakout + reclaim above support:
            Bear trap.
        """

        if (
            breakout is None
            or
            reclaim is None
        ):

            return TrapType.NONE

        if not breakout.detected:

            return TrapType.NONE

        if not reclaim.detected:

            return TrapType.NONE

        if (
            breakout.direction
            ==
            TrapDirection.BULLISH
            and
            reclaim.direction
            ==
            TrapDirection.BULLISH
        ):

            return TrapType.BULL_TRAP

        if (
            breakout.direction
            ==
            TrapDirection.BEARISH
            and
            reclaim.direction
            ==
            TrapDirection.BEARISH
        ):

            return TrapType.BEAR_TRAP

        return TrapType.NONE

    # =========================================================================
    # TRAP DIRECTION
    # =========================================================================

    @staticmethod
    def _trap_direction(
        trap_type: TrapType,
    ) -> TrapDirection:

        if (
            trap_type
            ==
            TrapType.BULL_TRAP
        ):

            return TrapDirection.BEARISH

        if (
            trap_type
            ==
            TrapType.BEAR_TRAP
        ):

            return TrapDirection.BULLISH

        return TrapDirection.NEUTRAL

    # =========================================================================
    # STATE
    # =========================================================================

    @staticmethod
    def _state(
        breakout: BreakoutEvent,
        reclaim: ReclaimEvent,
        rejection: RejectionEvent,
    ) -> TrapState:

        if (
            reclaim is not None
            and
            reclaim.detected
            and
            rejection is not None
            and
            rejection.detected
        ):

            return TrapState.CONFIRMED

        if (
            reclaim is not None
            and
            reclaim.detected
        ):

            return TrapState.RECLAIMED

        if (
            rejection is not None
            and
            rejection.detected
        ):

            return TrapState.REJECTION

        if (
            breakout is not None
            and
            breakout.detected
        ):

            return TrapState.BREAKOUT

        return TrapState.NONE

    # =========================================================================
    # SCORE
    # =========================================================================

    @staticmethod
    def _score(
        breakout: BreakoutEvent,
        reclaim: ReclaimEvent,
        rejection: RejectionEvent,
        volume: TrapVolumeEvidence,
        follow_through: FollowThroughFailure,
    ) -> float:
        """
        Calculate the raw evidence score.

        Maximum theoretical score = 6.

        Components:

            breakout
            reclaim
            rejection
            volume
            follow-through failure
            confirmed reversal/reclaim structure
        """

        score = 0.0

        # ---------------------------------------------------------------------
        # Breakout
        # ---------------------------------------------------------------------

        if (
            breakout is not None
            and
            breakout.detected
        ):

            score += 1.0

        # ---------------------------------------------------------------------
        # Reclaim
        # ---------------------------------------------------------------------

        if (
            reclaim is not None
            and
            reclaim.detected
        ):

            score += 1.0

        # ---------------------------------------------------------------------
        # Rejection
        # ---------------------------------------------------------------------

        if (
            rejection is not None
            and
            rejection.detected
        ):

            score += 1.0

        # ---------------------------------------------------------------------
        # Volume
        # ---------------------------------------------------------------------

        if (
            volume is not None
            and
            volume.available
            and
            volume.elevated
        ):

            score += 1.0

        # ---------------------------------------------------------------------
        # Follow-through failure
        # ---------------------------------------------------------------------

        if (
            follow_through is not None
            and
            follow_through.detected
        ):

            score += 1.0

        # ---------------------------------------------------------------------
        # Full structural confirmation
        # ---------------------------------------------------------------------

        if (
            reclaim is not None
            and
            reclaim.detected
            and
            rejection is not None
            and
            rejection.detected
        ):

            score += 1.0

        return min(
            6.0,
            score,
        )

    # =========================================================================
    # SIMPLE STATUS
    # =========================================================================

    def is_confirmed(
        self,
        result: TrapResult | None,
    ) -> bool:
        """
        Return True only when the final TrapResult meets COSMOS's
        confirmation requirements.
        """

        if result is None:

            return False

        return bool(
            result.valid
            and
            result.detected
            and
            result.score >= MIN_TRAP_SCORE
            and
            result.confidence
            >=
            HIGH_TRAP_CONFIDENCE
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

trap_engine = TrapEngine()


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def analyze_trap(
    candles,
    resistance: float | None = None,
    support: float | None = None,
    lookback: int = 20,
) -> TrapResult:
    """
    Convenience function for the rest of COSMOS.
    """

    return trap_engine.analyze(
        candles=candles,
        resistance=resistance,
        support=support,
        lookback=lookback,
    )
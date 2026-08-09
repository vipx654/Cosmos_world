"""
===============================================================================
COSMOS Trap Agent Probability Engine

Combines trap evidence into directional probability estimates.

Important:
    These values represent model confidence/evidence weighting.
    They are NOT guaranteed probabilities of profit.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.agents.trap.constants import (
    DEFAULT_TRAP_PROBABILITY,
    HIGH_TRAP_PROBABILITY,
    VERY_HIGH_TRAP_PROBABILITY,
)

from ai.agents.trap.models import (
    BreakoutEvent,
    ReclaimEvent,
    RejectionEvent,
    TrapCandidate,
    TrapProbability,
    TrapType,
    TrapDirection,
    TrapVolumeEvidence,
    FollowThroughFailure,
)


class TrapProbabilityEngine:
    """
    Converts trap evidence into directional probability estimates.
    """

    # =========================================================================
    # MAIN ANALYSIS
    # =========================================================================

    def analyze(
        self,
        candidate: TrapCandidate,
    ) -> TrapProbability:
        """
        Calculate probability estimates from a TrapCandidate.
        """

        if candidate is None:

            return TrapProbability()

        bullish_score = 0.0
        bearish_score = 0.0

        evidence: list[str] = []

        # ---------------------------------------------------------------------
        # Determine directional base
        # ---------------------------------------------------------------------

        if (
            candidate.trap_type
            ==
            TrapType.BULL_TRAP
        ):

            # A bull trap generally creates bearish reversal pressure.
            bearish_score += 30.0

            evidence.append(
                "Bull-trap structure contributes bearish probability"
            )

        elif (
            candidate.trap_type
            ==
            TrapType.BEAR_TRAP
        ):

            # A bear trap generally creates bullish reversal pressure.
            bullish_score += 30.0

            evidence.append(
                "Bear-trap structure contributes bullish probability"
            )

        # ---------------------------------------------------------------------
        # Reclaim evidence
        # ---------------------------------------------------------------------

        if (
            candidate.reclaim is not None
            and
            candidate.reclaim.detected
        ):

            strength = (
                candidate.reclaim.strength
            )

            if (
                candidate.trap_type
                ==
                TrapType.BULL_TRAP
            ):

                bearish_score += (
                    strength * 0.35
                )

            elif (
                candidate.trap_type
                ==
                TrapType.BEAR_TRAP
            ):

                bullish_score += (
                    strength * 0.35
                )

            evidence.append(
                "Level reclaim increases reversal probability"
            )

        # ---------------------------------------------------------------------
        # Rejection evidence
        # ---------------------------------------------------------------------

        if (
            candidate.rejection is not None
            and
            candidate.rejection.detected
        ):

            strength = (
                candidate.rejection.strength
            )

            if (
                candidate.trap_type
                ==
                TrapType.BULL_TRAP
            ):

                bearish_score += (
                    strength * 0.25
                )

            elif (
                candidate.trap_type
                ==
                TrapType.BEAR_TRAP
            ):

                bullish_score += (
                    strength * 0.25
                )

            evidence.append(
                "Rejection structure supports reversal direction"
            )

        # ---------------------------------------------------------------------
        # Volume evidence
        # ---------------------------------------------------------------------

        if (
            candidate.volume is not None
            and
            candidate.volume.available
        ):

            strength = (
                candidate.volume.strength
            )

            if (
                candidate.trap_type
                ==
                TrapType.BULL_TRAP
            ):

                bearish_score += (
                    strength * 0.15
                )

            elif (
                candidate.trap_type
                ==
                TrapType.BEAR_TRAP
            ):

                bullish_score += (
                    strength * 0.15
                )

            evidence.append(
                "Volume/activity evidence added to trap direction"
            )

        # ---------------------------------------------------------------------
        # Follow-through failure
        # ---------------------------------------------------------------------

        if (
            candidate.follow_through is not None
            and
            candidate.follow_through.detected
        ):

            strength = (
                candidate.follow_through.failure_strength
            )

            if (
                candidate.trap_type
                ==
                TrapType.BULL_TRAP
            ):

                bearish_score += (
                    strength * 0.25
                )

            elif (
                candidate.trap_type
                ==
                TrapType.BEAR_TRAP
            ):

                bullish_score += (
                    strength * 0.25
                )

            evidence.append(
                "Failure of continuation supports reversal"
            )

        # ---------------------------------------------------------------------
        # Clamp directional scores
        # ---------------------------------------------------------------------

        bullish_score = self._clamp(
            bullish_score
        )

        bearish_score = self._clamp(
            bearish_score
        )

        # ---------------------------------------------------------------------
        # Convert scores to probabilities
        # ---------------------------------------------------------------------

        bullish_probability = (
            DEFAULT_TRAP_PROBABILITY
            +
            bullish_score
            -
            bearish_score * 0.50
        )

        bearish_probability = (
            DEFAULT_TRAP_PROBABILITY
            +
            bearish_score
            -
            bullish_score * 0.50
        )

        bullish_probability = self._clamp(
            bullish_probability
        )

        bearish_probability = self._clamp(
            bearish_probability
        )

        # ---------------------------------------------------------------------
        # Neutral probability
        # ---------------------------------------------------------------------

        directional_strength = max(
            bullish_probability,
            bearish_probability,
        )

        neutral_probability = self._clamp(
            100.0
            -
            abs(
                bullish_probability
                -
                bearish_probability
            )
        )

        # ---------------------------------------------------------------------
        # Normalize relative directional probabilities
        # ---------------------------------------------------------------------

        total = (
            bullish_probability
            +
            bearish_probability
        )

        if total > 0.0:

            bullish_probability = (
                bullish_probability
                /
                total
                *
                100.0
            )

            bearish_probability = (
                bearish_probability
                /
                total
                *
                100.0
            )

        # ---------------------------------------------------------------------
        # Determine direction
        # ---------------------------------------------------------------------

        if (
            bearish_probability
            >
            bullish_probability
        ):

            direction = (
                TrapDirection.BEARISH
            )

        elif (
            bullish_probability
            >
            bearish_probability
        ):

            direction = (
                TrapDirection.BULLISH
            )

        else:

            direction = (
                TrapDirection.NEUTRAL
            )

        # ---------------------------------------------------------------------
        # Confidence
        # ---------------------------------------------------------------------

        confidence = self._confidence(
            candidate,
            directional_strength,
        )

        if confidence >= 85.0:

            evidence.append(
                "Very strong directional evidence"
            )

        elif confidence >= 70.0:

            evidence.append(
                "High directional evidence"
            )

        elif confidence >= 50.0:

            evidence.append(
                "Moderate directional evidence"
            )

        else:

            evidence.append(
                "Directional evidence remains limited"
            )

        return TrapProbability(

            direction=direction,

            trap_type=(
                candidate.trap_type
            ),

            bullish_probability=round(
                bullish_probability,
                2,
            ),

            bearish_probability=round(
                bearish_probability,
                2,
            ),

            neutral_probability=round(
                neutral_probability,
                2,
            ),

            confidence=round(
                confidence,
                2,
            ),

            evidence=evidence,
        )

    # =========================================================================
    # DIRECT EVIDENCE ANALYSIS
    # =========================================================================

    def from_evidence(
        self,
        breakout: BreakoutEvent | None = None,
        reclaim: ReclaimEvent | None = None,
        rejection: RejectionEvent | None = None,
        volume: TrapVolumeEvidence | None = None,
        follow_through: FollowThroughFailure | None = None,
        trap_type: TrapType = TrapType.NONE,
    ) -> TrapProbability:
        """
        Convenience interface for calculating probability without first
        constructing a TrapCandidate.
        """

        candidate = TrapCandidate(

            detected=True,

            trap_type=trap_type,

            direction=(
                TrapDirection.BEARISH
                if trap_type == TrapType.BULL_TRAP
                else
                TrapDirection.BULLISH
                if trap_type == TrapType.BEAR_TRAP
                else
                TrapDirection.NEUTRAL
            ),

            breakout=breakout,

            reclaim=reclaim,

            rejection=rejection,

            volume=volume,

            follow_through=follow_through,
        )

        return self.analyze(
            candidate
        )

    # =========================================================================
    # CONFIDENCE
    # =========================================================================

    @staticmethod
    def _confidence(
        candidate: TrapCandidate,
        directional_strength: float,
    ) -> float:
        """
        Estimate confidence from independent evidence components.
        """

        score = 0.0

        if (
            candidate.breakout is not None
            and
            candidate.breakout.detected
        ):

            score += 15.0

        if (
            candidate.reclaim is not None
            and
            candidate.reclaim.detected
        ):

            score += 25.0

        if (
            candidate.rejection is not None
            and
            candidate.rejection.detected
        ):

            score += 20.0

        if (
            candidate.volume is not None
            and
            candidate.volume.available
        ):

            score += 10.0

        if (
            candidate.follow_through is not None
            and
            candidate.follow_through.detected
        ):

            score += 20.0

        # Directional strength contributes only partially so that one
        # component cannot dominate the entire result.
        score += (
            directional_strength
            * 0.10
        )

        return max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

    # =========================================================================
    # CLAMP
    # =========================================================================

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                float(value),
            ),
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

trap_probability_engine = TrapProbabilityEngine()
"""
===============================================================================
COSMOS Strategy Agent

Combines signals from the completed market-analysis agents into a unified
trade proposal.

IMPORTANT:
    This agent DOES NOT:
        - calculate final account risk
        - override risk limits
        - place orders
        - modify broker positions

Pipeline:

    Analysis Agents
          ↓
    Strategy Agent
          ↓
    TradeProposal
          ↓
    Session Agent
          ↓
    Risk Agent
          ↓
    Execution Agent

Author: COSMOS Development Team
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# =============================================================================
# ENUMS
# =============================================================================

class TradeDirection(str, Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


class StrategyAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    WAIT = "wait"


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class SignalEvidence:
    name: str
    direction: TradeDirection
    strength: float
    active: bool = True
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class TradeProposal:
    """
    Output contract consumed by Session/Risk/Execution agents.
    """

    action: StrategyAction = StrategyAction.WAIT

    direction: TradeDirection = (
        TradeDirection.NEUTRAL
    )

    symbol: str = ""

    entry: float | None = None

    stop_loss: float | None = None

    take_profit: float | None = None

    confidence: float = 0.0

    score: float = 0.0

    reward_risk: float = 0.0

    evidence: list[SignalEvidence] = field(
        default_factory=list
    )

    reasons: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =============================================================================
# STRATEGY ENGINE
# =============================================================================

class StrategyEngine:

    """
    COSMOS decision layer.

    The completed specialist agents provide evidence.
    This engine determines whether those pieces form a coherent setup.
    """

    # Minimum evidence required before proposing a trade.
    MIN_SCORE = 55.0

    # Minimum directional confidence.
    MIN_CONFIDENCE = 60.0

    def analyze(
        self,
        symbol: str,
        *,
        trend: Any = None,
        smc: Any = None,
        sweep: Any = None,
        order_block: Any = None,
        market_structure: Any = None,
        liquidity: Any = None,
        fvg: Any = None,
        volume: Any = None,
        trap: Any = None,
        price: float | None = None,
    ) -> TradeProposal:

        evidence: list[
            SignalEvidence
        ] = []

        reasons: list[str] = []

        # =====================================================================
        # COLLECT SPECIALIST SIGNALS
        # =====================================================================

        evidence.extend(
            self._extract(
                "trend",
                trend,
            )
        )

        evidence.extend(
            self._extract(
                "smc",
                smc,
            )
        )

        evidence.extend(
            self._extract(
                "sweep",
                sweep,
            )
        )

        evidence.extend(
            self._extract(
                "order_block",
                order_block,
            )
        )

        evidence.extend(
            self._extract(
                "market_structure",
                market_structure,
            )
        )

        evidence.extend(
            self._extract(
                "liquidity",
                liquidity,
            )
        )

        evidence.extend(
            self._extract(
                "fvg",
                fvg,
            )
        )

        evidence.extend(
            self._extract(
                "volume",
                volume,
            )
        )

        evidence.extend(
            self._extract(
                "trap",
                trap,
            )
        )

        # =====================================================================
        # REMOVE INACTIVE SIGNALS
        # =====================================================================

        active = [
            item
            for item in evidence
            if item.active
        ]

        if not active:

            return TradeProposal(
                symbol=symbol,
                reasons=[
                    "No active specialist signals"
                ],
            )

        # =====================================================================
        # DIRECTIONAL SCORING
        # =====================================================================

        bullish_score = 0.0
        bearish_score = 0.0

        for item in active:

            strength = self._clamp(
                item.strength
            )

            if (
                item.direction
                == TradeDirection.LONG
            ):

                bullish_score += strength

            elif (
                item.direction
                == TradeDirection.SHORT
            ):

                bearish_score += strength

        # Normalize accumulated evidence.
        bullish_score = self._normalize(
            bullish_score
        )

        bearish_score = self._normalize(
            bearish_score
        )

        # =====================================================================
        # TRAP OVERRIDE / WARNING
        # =====================================================================

        trap_direction = (
            self._direction_from_result(
                trap
            )
        )

        if (
            trap_direction
            !=
            TradeDirection.NEUTRAL
        ):

            trap_strength = self._strength(
                trap
            )

            if (
                trap_strength
                >=
                70.0
            ):

                # A confirmed bull trap is bearish.
                # A confirmed bear trap is bullish.
                if (
                    trap_direction
                    == TradeDirection.SHORT
                ):

                    bearish_score += (
                        trap_strength
                        * 0.25
                    )

                    reasons.append(
                        "Trap evidence supports short direction"
                    )

                elif (
                    trap_direction
                    == TradeDirection.LONG
                ):

                    bullish_score += (
                        trap_strength
                        * 0.25
                    )

                    reasons.append(
                        "Trap evidence supports long direction"
                    )

        # =====================================================================
        # FINAL NORMALIZATION
        # =====================================================================

        bullish_score = self._normalize(
            bullish_score
        )

        bearish_score = self._normalize(
            bearish_score
        )

        if (
            bullish_score
            >
            bearish_score
        ):

            direction = (
                TradeDirection.LONG
            )

            score = bullish_score

        elif (
            bearish_score
            >
            bullish_score
        ):

            direction = (
                TradeDirection.SHORT
            )

            score = bearish_score

        else:

            direction = (
                TradeDirection.NEUTRAL
            )

            score = 0.0

        # =====================================================================
        # CONFLICT DETECTION
        # =====================================================================

        conflict = (
            bullish_score >= 45.0
            and
            bearish_score >= 45.0
        )

        if conflict:

            reasons.append(
                "Specialist agents show conflicting directional evidence"
            )

            return TradeProposal(
                symbol=symbol,
                action=StrategyAction.WAIT,
                direction=TradeDirection.NEUTRAL,
                confidence=0.0,
                score=round(
                    score,
                    2,
                ),
                evidence=active,
                reasons=reasons,
                metadata={
                    "bullish_score": bullish_score,
                    "bearish_score": bearish_score,
                    "conflict": True,
                },
            )

        # =====================================================================
        # CONFIDENCE
        # =====================================================================

        confidence = self._confidence(
            active,
            score,
            direction,
        )

        # =====================================================================
        # ENTRY
        # =====================================================================

        entry = self._entry_price(
            price,
            direction,
            active,
        )

        # =====================================================================
        # WAIT CONDITION
        # =====================================================================

        if (
            score
            <
            self.MIN_SCORE
            or
            confidence
            <
            self.MIN_CONFIDENCE
            or
            direction
            ==
            TradeDirection.NEUTRAL
        ):

            reasons.append(
                "Evidence does not meet strategy confirmation threshold"
            )

            return TradeProposal(
                symbol=symbol,
                action=StrategyAction.WAIT,
                direction=direction,
                entry=entry,
                confidence=round(
                    confidence,
                    2,
                ),
                score=round(
                    score,
                    2,
                ),
                evidence=active,
                reasons=reasons,
                metadata={
                    "bullish_score": bullish_score,
                    "bearish_score": bearish_score,
                },
            )

        # =====================================================================
        # TRADE ACTION
        # =====================================================================

        if direction == TradeDirection.LONG:

            action = StrategyAction.BUY

            reasons.append(
                "Bullish evidence stack confirmed"
            )

        else:

            action = StrategyAction.SELL

            reasons.append(
                "Bearish evidence stack confirmed"
            )

        # =====================================================================
        # STRUCTURAL LEVELS
        # =====================================================================

        stop_loss = self._stop_from_evidence(
            active,
            direction,
        )

        take_profit = self._target_from_evidence(
            active,
            direction,
        )

        reward_risk = self._reward_risk(
            entry,
            stop_loss,
            take_profit,
        )

        # =====================================================================
        # FINAL PROPOSAL
        # =====================================================================

        return TradeProposal(

            action=action,

            direction=direction,

            symbol=symbol,

            entry=entry,

            stop_loss=stop_loss,

            take_profit=take_profit,

            confidence=round(
                confidence,
                2,
            ),

            score=round(
                score,
                2,
            ),

            reward_risk=round(
                reward_risk,
                3,
            ),

            evidence=active,

            reasons=reasons,

            metadata={
                "bullish_score": bullish_score,
                "bearish_score": bearish_score,
                "specialist_count": len(active),
                "risk_authority": "risk_agent",
                "execution_authority": "execution_agent",
            },
        )

    # =========================================================================
    # SIGNAL EXTRACTION
    # =========================================================================

    def _extract(
        self,
        name: str,
        result: Any,
    ) -> list[SignalEvidence]:

        if result is None:

            return []

        direction = (
            self._direction_from_result(
                result
            )
        )

        strength = (
            self._strength(
                result
            )
        )

        active = (
            direction
            !=
            TradeDirection.NEUTRAL
            and
            strength > 0.0
        )

        return [
            SignalEvidence(
                name=name,
                direction=direction,
                strength=strength,
                active=active,
                metadata={
                    "source_type": type(
                        result
                    ).__name__,
                },
            )
        ]

    # =========================================================================
    # DIRECTION
    # =========================================================================

    @staticmethod
    def _direction_from_result(
        result: Any,
    ) -> TradeDirection:

        if result is None:

            return TradeDirection.NEUTRAL

        raw = getattr(
            result,
            "direction",
            None,
        )

        if raw is None:

            raw = getattr(
                result,
                "bias",
                None,
            )

        if raw is None:

            return TradeDirection.NEUTRAL

        value = str(
            getattr(
                raw,
                "value",
                raw,
            )
        ).lower()

        if value in (
            "bullish",
            "long",
            "buy",
            "up",
        ):

            return TradeDirection.LONG

        if value in (
            "bearish",
            "short",
            "sell",
            "down",
        ):

            return TradeDirection.SHORT

        return TradeDirection.NEUTRAL

    # =========================================================================
    # STRENGTH
    # =========================================================================

    @staticmethod
    def _strength(
        result: Any,
    ) -> float:

        if result is None:

            return 0.0

        for field_name in (
            "confidence",
            "strength",
            "score",
            "probability",
        ):

            value = getattr(
                result,
                field_name,
                None,
            )

            if value is not None:

                try:

                    value = float(
                        value
                    )

                    if value <= 1.0:

                        value *= 100.0

                    return max(
                        0.0,
                        min(
                            100.0,
                            value,
                        ),
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    continue

        return 0.0

    # =========================================================================
    # CONFIDENCE
    # =========================================================================

    @staticmethod
    def _confidence(
        evidence: list[SignalEvidence],
        directional_score: float,
        direction: TradeDirection,
    ) -> float:

        if not evidence:

            return 0.0

        aligned = [
            item
            for item in evidence
            if (
                item.direction
                ==
                direction
            )
        ]

        alignment_ratio = (
            len(aligned)
            /
            len(evidence)
        )

        confidence = (
            directional_score * 0.60
            +
            alignment_ratio * 40.0
        )

        return max(
            0.0,
            min(
                100.0,
                confidence,
            ),
        )

    # =========================================================================
    # ENTRY
    # =========================================================================

    @staticmethod
    def _entry_price(
        price: float | None,
        direction: TradeDirection,
        evidence: list[SignalEvidence],
    ) -> float | None:

        if price is None:

            return None

        try:

            return float(price)

        except (
            TypeError,
            ValueError,
        ):

            return None

    # =========================================================================
    # STOP
    # =========================================================================

    @staticmethod
    def _stop_from_evidence(
        evidence: list[SignalEvidence],
        direction: TradeDirection,
    ) -> float | None:

        """
        Strategy can suggest a structural stop.

        Risk Agent remains the authority that validates the stop.
        """

        levels = []

        for item in evidence:

            level = item.metadata.get(
                "stop_loss"
            )

            if level is not None:

                try:

                    levels.append(
                        float(level)
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    pass

        if not levels:

            return None

        if direction == TradeDirection.LONG:

            return min(levels)

        if direction == TradeDirection.SHORT:

            return max(levels)

        return None

    # =========================================================================
    # TARGET
    # =========================================================================

    @staticmethod
    def _target_from_evidence(
        evidence: list[SignalEvidence],
        direction: TradeDirection,
    ) -> float | None:

        levels = []

        for item in evidence:

            level = item.metadata.get(
                "take_profit"
            )

            if level is not None:

                try:

                    levels.append(
                        float(level)
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    pass

        if not levels:

            return None

        if direction == TradeDirection.LONG:

            return max(levels)

        if direction == TradeDirection.SHORT:

            return min(levels)

        return None

    # =========================================================================
    # REWARD / RISK
    # =========================================================================

    @staticmethod
    def _reward_risk(
        entry: float | None,
        stop: float | None,
        target: float | None,
    ) -> float:

        if (
            entry is None
            or
            stop is None
            or
            target is None
        ):

            return 0.0

        risk = abs(
            entry - stop
        )

        reward = abs(
            target - entry
        )

        if risk <= 0.0:

            return 0.0

        return reward / risk

    # =========================================================================
    # NORMALIZATION
    # =========================================================================

    @staticmethod
    def _normalize(
        value: float,
    ) -> float:

        # Nine specialist agents can contribute.
        # Convert accumulated strength to a 0-100 score.
        return max(
            0.0,
            min(
                100.0,
                float(value)
                /
                9.0,
            ),
        )

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

strategy_engine = StrategyEngine()


# =============================================================================
# PUBLIC API
# =============================================================================

def analyze_strategy(
    symbol: str,
    **signals: Any,
) -> TradeProposal:

    return strategy_engine.analyze(
        symbol,
        **signals,
    )
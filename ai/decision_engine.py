"""
===============================================================================
COSMOS Decision Engine

Combines outputs from all AI agents into a single trading decision.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from __future__ import annotations

from ai.memory import memory


class DecisionEngine:
    """
    AI Fusion Engine.

    Reads every agent's output from shared memory and
    produces the final BUY / SELL / HOLD decision.
    """

    def __init__(self):

        self.buy_score = 0.0
        self.sell_score = 0.0
        self.neutral_score = 0.0

    # ------------------------------------------------------------------

    def evaluate(self) -> dict:

        self.buy_score = 0.0
        self.sell_score = 0.0
        self.neutral_score = 0.0

        agents = memory.all()

        if not agents:

            return {
                "decision": "HOLD",
                "confidence": 0.0,
                "buy_score": 0.0,
                "sell_score": 0.0,
                "neutral_score": 0.0,
            }

        for agent in agents:

            signal = agent.signal.upper()

            confidence = float(agent.confidence)

            if signal == "BUY":
                self.buy_score += confidence

            elif signal == "SELL":
                self.sell_score += confidence

            else:
                self.neutral_score += confidence

        total = (
            self.buy_score
            + self.sell_score
            + self.neutral_score
        )

        if total == 0:

            return {
                "decision": "HOLD",
                "confidence": 0.0,
                "buy_score": 0.0,
                "sell_score": 0.0,
                "neutral_score": 0.0,
            }

        buy_percent = (self.buy_score / total) * 100
        sell_percent = (self.sell_score / total) * 100

        if buy_percent > sell_percent:

            decision = "BUY"
            confidence = round(buy_percent, 2)

        elif sell_percent > buy_percent:

            decision = "SELL"
            confidence = round(sell_percent, 2)

        else:

            decision = "HOLD"
            confidence = 50.0

        return {

            "decision": decision,

            "confidence": confidence,

            "buy_score": round(self.buy_score, 2),

            "sell_score": round(self.sell_score, 2),

            "neutral_score": round(
                self.neutral_score,
                2,
            ),

            "agents": memory.summary(),
        }


decision_engine = DecisionEngine()
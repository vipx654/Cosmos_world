"""
===============================================================================
COSMOS Risk Agent

Central pre-trade and account-risk control layer.

Pipeline:

    Strategy Proposal
          ↓
    Session Context
          ↓
    Account State
          ↓
    Risk Engine
       ┌──┴───────────────┐
       ▼                  ▼
    APPROVE             REJECT
       │
       ▼
    Execution Agent

The Risk Agent:
    - calculates permitted monetary risk
    - calculates position size
    - checks stop-loss validity
    - checks reward/risk
    - checks daily loss
    - checks drawdown
    - checks open-position limits
    - checks exposure
    - provides a kill-switch
    - NEVER sends an order to a broker

Author: COSMOS Development Team
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import floor
from typing import Any


# =============================================================================
# ENUMS
# =============================================================================

class RiskDecision(str, Enum):
    APPROVE = "approve"
    REDUCE = "reduce"
    REJECT = "reject"
    HALT = "halt"


class RiskSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class RiskConfig:
    """
    Default risk configuration.

    These are conservative software defaults, not a recommendation for a
    particular trading account or prop-firm rule set.
    """

    risk_per_trade_pct: float = 0.50

    max_risk_per_trade_pct: float = 1.00

    max_daily_loss_pct: float = 2.00

    max_drawdown_pct: float = 5.00

    max_open_positions: int = 3

    max_total_risk_pct: float = 2.00

    min_reward_risk: float = 1.50

    min_stop_distance: float = 0.0

    max_position_size: float = 100.0

    min_position_size: float = 0.01

    volume_step: float = 0.01

    max_consecutive_losses: int = 4

    require_stop_loss: bool = True

    allow_reduce_size: bool = True


# =============================================================================
# ACCOUNT STATE
# =============================================================================

@dataclass
class AccountState:
    """
    Runtime account state supplied by broker/account adapter.
    """

    balance: float = 0.0

    equity: float = 0.0

    peak_equity: float = 0.0

    daily_start_equity: float = 0.0

    daily_pnl: float = 0.0

    floating_pnl: float = 0.0

    open_positions: int = 0

    open_risk_amount: float = 0.0

    consecutive_losses: int = 0

    halted: bool = False

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =============================================================================
# RISK RESULT
# =============================================================================

@dataclass
class RiskResult:
    """
    Output contract consumed by Execution Agent.
    """

    decision: RiskDecision = (
        RiskDecision.REJECT
    )

    approved: bool = False

    symbol: str = ""

    requested_size: float = 0.0

    approved_size: float = 0.0

    risk_amount: float = 0.0

    risk_percent: float = 0.0

    stop_distance: float = 0.0

    reward_risk: float = 0.0

    daily_loss_pct: float = 0.0

    drawdown_pct: float = 0.0

    total_open_risk_pct: float = 0.0

    severity: RiskSeverity = (
        RiskSeverity.INFO
    )

    reasons: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =============================================================================
# RISK ENGINE
# =============================================================================

class RiskEngine:

    def __init__(
        self,
        config: RiskConfig | None = None,
    ) -> None:

        self.config = (
            config
            or
            RiskConfig()
        )

        self._halted = False

    # =========================================================================
    # MAIN API
    # =========================================================================

    def evaluate(
        self,
        proposal: Any,
        account: AccountState,
        *,
        entry: float | None = None,
        stop_loss: float | None = None,
        take_profit: float | None = None,
        requested_size: float | None = None,
        value_per_price_unit: float = 1.0,
        session: Any = None,
    ) -> RiskResult:
        """
        Perform complete pre-trade risk evaluation.

        `value_per_price_unit` must be supplied by the instrument/broker
        adapter when the symbol's monetary value per price unit differs from
        one account-currency unit.
        """

        symbol = str(
            getattr(
                proposal,
                "symbol",
                "",
            )
            or
            ""
        )

        reasons: list[str] = []

        warnings: list[str] = []

        # =====================================================================
        # KILL SWITCH
        # =====================================================================

        if (
            self._halted
            or
            account.halted
        ):

            return self._reject(
                symbol,
                RiskDecision.HALT,
                "Risk kill-switch is active",
                severity=RiskSeverity.CRITICAL,
            )

        # =====================================================================
        # BASIC ACCOUNT VALIDATION
        # =====================================================================

        if account.equity <= 0.0:

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Account equity must be positive",
                severity=RiskSeverity.CRITICAL,
            )

        # =====================================================================
        # PROPOSAL VALIDATION
        # =====================================================================

        if proposal is None:

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "No strategy proposal supplied",
            )

        proposal_direction = str(
            getattr(
                getattr(
                    proposal,
                    "direction",
                    None,
                ),
                "value",
                getattr(
                    proposal,
                    "direction",
                    "",
                ),
            )
        ).lower()

        if proposal_direction not in (
            "long",
            "short",
            "bullish",
            "bearish",
        ):

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Strategy proposal has no valid trade direction",
            )

        # =====================================================================
        # SESSION CHECK
        # =====================================================================

        if session is not None:

            tradable = getattr(
                session,
                "tradable",
                True,
            )

            if not tradable:

                return self._reject(
                    symbol,
                    RiskDecision.REJECT,
                    "Session is not currently tradable",
                )

            session_score = float(
                getattr(
                    session,
                    "session_score",
                    100.0,
                )
                or
                0.0
            )

            if session_score < 30.0:

                warnings.append(
                    "Session quality is weak"
                )

        # =====================================================================
        # DAILY LOSS
        # =====================================================================

        daily_loss_pct = self._daily_loss_pct(
            account
        )

        if (
            daily_loss_pct
            >=
            self.config.max_daily_loss_pct
        ):

            self.activate_kill_switch()

            return self._reject(
                symbol,
                RiskDecision.HALT,
                "Maximum daily loss limit reached",
                severity=RiskSeverity.CRITICAL,
                daily_loss_pct=daily_loss_pct,
            )

        # =====================================================================
        # DRAWDOWN
        # =====================================================================

        drawdown_pct = self._drawdown_pct(
            account
        )

        if (
            drawdown_pct
            >=
            self.config.max_drawdown_pct
        ):

            self.activate_kill_switch()

            return self._reject(
                symbol,
                RiskDecision.HALT,
                "Maximum account drawdown reached",
                severity=RiskSeverity.CRITICAL,
                daily_loss_pct=daily_loss_pct,
                drawdown_pct=drawdown_pct,
            )

        # =====================================================================
        # CONSECUTIVE LOSSES
        # =====================================================================

        if (
            account.consecutive_losses
            >=
            self.config.max_consecutive_losses
        ):

            return self._reject(
                symbol,
                RiskDecision.HALT,
                "Maximum consecutive losses reached",
                severity=RiskSeverity.CRITICAL,
                daily_loss_pct=daily_loss_pct,
                drawdown_pct=drawdown_pct,
            )

        # =====================================================================
        # OPEN POSITION LIMIT
        # =====================================================================

        if (
            account.open_positions
            >=
            self.config.max_open_positions
        ):

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Maximum open-position limit reached",
                daily_loss_pct=daily_loss_pct,
                drawdown_pct=drawdown_pct,
            )

        # =====================================================================
        # PRICE LEVELS
        # =====================================================================

        if entry is None:

            entry = getattr(
                proposal,
                "entry",
                None,
            )

        if stop_loss is None:

            stop_loss = getattr(
                proposal,
                "stop_loss",
                None,
            )

        if take_profit is None:

            take_profit = getattr(
                proposal,
                "take_profit",
                None,
            )

        if entry is None:

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Entry price is missing",
            )

        entry = float(entry)

        # =====================================================================
        # STOP LOSS
        # =====================================================================

        if (
            self.config.require_stop_loss
            and
            stop_loss is None
        ):

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Stop-loss is required",
            )

        if stop_loss is None:

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Cannot calculate risk without stop-loss",
            )

        stop_loss = float(
            stop_loss
        )

        stop_distance = abs(
            entry - stop_loss
        )

        if (
            stop_distance
            <=
            self.config.min_stop_distance
        ):

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Stop-loss distance is invalid",
            )

        # =====================================================================
        # STOP DIRECTION VALIDATION
        # =====================================================================

        if (
            proposal_direction
            in (
                "long",
                "bullish",
            )
            and
            stop_loss >= entry
        ):

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Long trade requires stop-loss below entry",
            )

        if (
            proposal_direction
            in (
                "short",
                "bearish",
            )
            and
            stop_loss <= entry
        ):

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Short trade requires stop-loss above entry",
            )

        # =====================================================================
        # REWARD / RISK
        # =====================================================================

        reward_risk = 0.0

        if take_profit is not None:

            take_profit = float(
                take_profit
            )

            reward = abs(
                take_profit
                -
                entry
            )

            reward_risk = (
                reward
                /
                stop_distance
            )

            if (
                reward_risk
                <
                self.config.min_reward_risk
            ):

                return self._reject(
                    symbol,
                    RiskDecision.REJECT,
                    "Reward/risk ratio is below minimum",
                    daily_loss_pct=daily_loss_pct,
                    drawdown_pct=drawdown_pct,
                    reward_risk=reward_risk,
                )

        # =====================================================================
        # RISK BUDGET
        # =====================================================================

        requested_risk_pct = min(
            self.config.risk_per_trade_pct,
            self.config.max_risk_per_trade_pct,
        )

        risk_budget = (
            account.equity
            *
            requested_risk_pct
            /
            100.0
        )

        # Remaining portfolio risk budget.
        total_risk_limit = (
            account.equity
            *
            self.config.max_total_risk_pct
            /
            100.0
        )

        remaining_risk = max(
            0.0,
            total_risk_limit
            -
            max(
                0.0,
                account.open_risk_amount,
            ),
        )

        # =====================================================================
        # POSITION SIZE
        # =====================================================================

        if value_per_price_unit <= 0.0:

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Invalid monetary value-per-price-unit",
            )

        calculated_size = (
            risk_budget
            /
            (
                stop_distance
                *
                value_per_price_unit
            )
        )

        requested = (
            calculated_size
            if requested_size is None
            else float(
                requested_size
            )
        )

        requested = min(
            requested,
            self.config.max_position_size,
        )

        # =====================================================================
        # EXISTING EXPOSURE LIMIT
        # =====================================================================

        remaining_size = (
            remaining_risk
            /
            (
                stop_distance
                *
                value_per_price_unit
            )
        )

        approved_size = min(
            requested,
            calculated_size,
            remaining_size,
        )

        # =====================================================================
        # ROUND TO BROKER STEP
        # =====================================================================

        approved_size = self._floor_step(
            approved_size,
            self.config.volume_step,
        )

        if (
            approved_size
            <
            self.config.min_position_size
        ):

            return self._reject(
                symbol,
                RiskDecision.REJECT,
                "Calculated position size is below broker minimum",
                daily_loss_pct=daily_loss_pct,
                drawdown_pct=drawdown_pct,
                reward_risk=reward_risk,
            )

        # =====================================================================
        # FINAL RISK
        # =====================================================================

        final_risk_amount = (
            approved_size
            *
            stop_distance
            *
            value_per_price_unit
        )

        final_risk_pct = (
            final_risk_amount
            /
            account.equity
            *
            100.0
        )

        # =====================================================================
        # REDUCTION
        # =====================================================================

        reduced = (
            approved_size
            <
            requested
        )

        if reduced:

            if not self.config.allow_reduce_size:

                return self._reject(
                    symbol,
                    RiskDecision.REJECT,
                    "Requested size exceeds risk budget",
                    daily_loss_pct=daily_loss_pct,
                    drawdown_pct=drawdown_pct,
                    reward_risk=reward_risk,
                )

            reasons.append(
                "Position size reduced to fit risk limits"
            )

            decision = RiskDecision.REDUCE

        else:

            decision = RiskDecision.APPROVE

            reasons.append(
                "Trade passed all pre-trade risk checks"
            )

        # =====================================================================
        # WARNINGS
        # =====================================================================

        if (
            final_risk_pct
            >=
            self.config.max_risk_per_trade_pct
            *
            0.80
        ):

            warnings.append(
                "Trade is close to maximum per-trade risk"
            )

        if (
            drawdown_pct
            >=
            self.config.max_drawdown_pct
            *
            0.75
        ):

            warnings.append(
                "Account drawdown is approaching the hard limit"
            )

        # =====================================================================
        # RESULT
        # =====================================================================

        return RiskResult(

            decision=decision,

            approved=True,

            symbol=symbol,

            requested_size=round(
                requested,
                8,
            ),

            approved_size=round(
                approved_size,
                8,
            ),

            risk_amount=round(
                final_risk_amount,
                8,
            ),

            risk_percent=round(
                final_risk_pct,
                4,
            ),

            stop_distance=round(
                stop_distance,
                8,
            ),

            reward_risk=round(
                reward_risk,
                4,
            ),

            daily_loss_pct=round(
                daily_loss_pct,
                4,
            ),

            drawdown_pct=round(
                drawdown_pct,
                4,
            ),

            total_open_risk_pct=round(
                (
                    account.open_risk_amount
                    /
                    account.equity
                    *
                    100.0
                ),
                4,
            ),

            severity=(
                RiskSeverity.WARNING
                if reduced
                else RiskSeverity.INFO
            ),

            reasons=reasons,

            warnings=warnings,

            metadata={
                "risk_budget": risk_budget,
                "remaining_risk_budget": remaining_risk,
                "value_per_price_unit": value_per_price_unit,
                "max_position_size": (
                    self.config.max_position_size
                ),
                "risk_authority": True,
                "execution_authority": False,
            },
        )

    # =========================================================================
    # DAILY LOSS
    # =========================================================================

    @staticmethod
    def _daily_loss_pct(
        account: AccountState,
    ) -> float:

        if (
            account.daily_start_equity
            <=
            0.0
        ):

            return 0.0

        loss = max(
            0.0,
            account.daily_start_equity
            -
            account.equity,
        )

        return (
            loss
            /
            account.daily_start_equity
            *
            100.0
        )

    # =========================================================================
    # DRAWDOWN
    # =========================================================================

    @staticmethod
    def _drawdown_pct(
        account: AccountState,
    ) -> float:

        peak = max(
            account.peak_equity,
            account.equity,
        )

        if peak <= 0.0:

            return 0.0

        return (
            max(
                0.0,
                peak
                -
                account.equity,
            )
            /
            peak
            *
            100.0
        )

    # =========================================================================
    # KILL SWITCH
    # =========================================================================

    def activate_kill_switch(self) -> None:

        self._halted = True

    def reset_kill_switch(self) -> None:

        self._halted = False

    @property
    def halted(self) -> bool:

        return self._halted

    # =========================================================================
    # FLOOR TO BROKER STEP
    # =========================================================================

    @staticmethod
    def _floor_step(
        value: float,
        step: float,
    ) -> float:

        if step <= 0.0:

            return value

        units = floor(
            value / step
        )

        return units * step

    # =========================================================================
    # REJECTION HELPER
    # =========================================================================

    @staticmethod
    def _reject(
        symbol: str,
        decision: RiskDecision,
        reason: str,
        *,
        severity: RiskSeverity = (
            RiskSeverity.WARNING
        ),
        daily_loss_pct: float = 0.0,
        drawdown_pct: float = 0.0,
        reward_risk: float = 0.0,
    ) -> RiskResult:

        return RiskResult(

            decision=decision,

            approved=False,

            symbol=symbol,

            requested_size=0.0,

            approved_size=0.0,

            risk_amount=0.0,

            risk_percent=0.0,

            daily_loss_pct=round(
                daily_loss_pct,
                4,
            ),

            drawdown_pct=round(
                drawdown_pct,
                4,
            ),

            reward_risk=round(
                reward_risk,
                4,
            ),

            severity=severity,

            reasons=[reason],

            metadata={
                "execution_allowed": False,
            },
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

risk_engine = RiskEngine()


# =============================================================================
# PUBLIC API
# =============================================================================

def evaluate_risk(
    proposal: Any,
    account: AccountState,
    **kwargs: Any,
) -> RiskResult:

    return risk_engine.evaluate(
        proposal,
        account,
        **kwargs,
    )
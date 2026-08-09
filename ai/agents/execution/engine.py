"""
===============================================================================
COSMOS Execution Agent

Final gateway between approved RiskResult objects and a broker adapter.

IMPORTANT:
    This layer NEVER bypasses Risk.

Pipeline:

    Strategy
       ↓
    Session
       ↓
    Risk
       ↓
    Execution
       ↓
    Broker Adapter
       ↓
    Broker

Responsibilities:
    - validate RiskResult
    - validate order parameters
    - validate price deviation
    - validate maximum order size
    - prevent duplicate execution
    - throttle execution
    - support dry-run/paper mode
    - submit through broker adapter
    - normalize broker responses
    - maintain emergency kill switch

The broker-specific implementation is injected through BrokerAdapter.

Author: COSMOS Development Team
===============================================================================
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Any, Protocol


# =============================================================================
# ENUMS
# =============================================================================

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class ExecutionStatus(str, Enum):
    ACCEPTED = "accepted"
    FILLED = "filled"
    PARTIAL = "partial"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DRY_RUN = "dry_run"


# =============================================================================
# ORDER
# =============================================================================

@dataclass
class OrderRequest:
    symbol: str

    side: OrderSide

    order_type: OrderType

    quantity: float

    entry_price: float | None = None

    stop_loss: float | None = None

    take_profit: float | None = None

    client_order_id: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =============================================================================
# RESULT
# =============================================================================

@dataclass
class ExecutionResult:
    status: ExecutionStatus

    success: bool

    symbol: str

    client_order_id: str

    broker_order_id: str | None = None

    requested_quantity: float = 0.0

    executed_quantity: float = 0.0

    requested_price: float | None = None

    executed_price: float | None = None

    stop_loss: float | None = None

    take_profit: float | None = None

    slippage: float = 0.0

    reason: str = ""

    warnings: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =============================================================================
# BROKER ADAPTER
# =============================================================================

class BrokerAdapter(Protocol):

    def get_quote(
        self,
        symbol: str,
    ) -> dict[str, float]:
        ...

    def submit_order(
        self,
        order: OrderRequest,
    ) -> dict[str, Any]:
        ...

    def cancel_order(
        self,
        broker_order_id: str,
    ) -> bool:
        ...

    def close_position(
        self,
        symbol: str,
        quantity: float | None = None,
    ) -> dict[str, Any]:
        ...


# =============================================================================
# CONFIG
# =============================================================================

@dataclass
class ExecutionConfig:

    dry_run: bool = True

    max_order_quantity: float = 100.0

    max_price_deviation_pct: float = 0.50

    min_execution_interval_seconds: float = 1.0

    max_orders_per_window: int = 10

    execution_window_seconds: float = 60.0

    require_stop_loss: bool = True

    allow_market_orders: bool = True

    allow_limit_orders: bool = True

    allow_stop_orders: bool = True


# =============================================================================
# ENGINE
# =============================================================================

class ExecutionEngine:

    def __init__(
        self,
        broker: BrokerAdapter | None = None,
        config: ExecutionConfig | None = None,
    ) -> None:

        self.broker = broker

        self.config = (
            config
            or
            ExecutionConfig()
        )

        self._halted = False

        self._lock = Lock()

        self._recent_executions: list[
            float
        ] = []

        self._executed_ids: set[
            str
        ] = set()

    # =========================================================================
    # MAIN API
    # =========================================================================

    def execute(
        self,
        risk_result: Any,
        *,
        order: OrderRequest | None = None,
    ) -> ExecutionResult:

        if risk_result is None:

            return self._reject(
                "",
                "",
                "Risk result is missing",
            )

        symbol = str(
            getattr(
                risk_result,
                "symbol",
                "",
            )
            or
            ""
        )

        # =====================================================================
        # KILL SWITCH
        # =====================================================================

        if self._halted:

            return self._reject(
                symbol,
                "",
                "Execution kill-switch is active",
                ExecutionStatus.CANCELLED,
            )

        # =====================================================================
        # RISK APPROVAL
        # =====================================================================

        approved = bool(
            getattr(
                risk_result,
                "approved",
                False,
            )
        )

        if not approved:

            return self._reject(
                symbol,
                "",
                "Risk Agent did not approve the trade",
            )

        # =====================================================================
        # CREATE ORDER
        # =====================================================================

        if order is None:

            order = self._order_from_risk(
                risk_result
            )

        # =====================================================================
        # ORDER VALIDATION
        # =====================================================================

        validation_error = (
            self._validate_order(
                order
            )
        )

        if validation_error:

            return self._reject(
                order.symbol,
                order.client_order_id,
                validation_error,
            )

        # =====================================================================
        # DUPLICATE PROTECTION
        # =====================================================================

        with self._lock:

            if (
                order.client_order_id
                in
                self._executed_ids
            ):

                return self._reject(
                    order.symbol,
                    order.client_order_id,
                    "Duplicate client order ID",
                )

        # =====================================================================
        # RATE LIMIT
        # =====================================================================

        if not self._execution_allowed():

            return self._reject(
                order.symbol,
                order.client_order_id,
                "Execution throttle limit reached",
            )

        # =====================================================================
        # DRY RUN
        # =====================================================================

        if self.config.dry_run:

            with self._lock:

                self._executed_ids.add(
                    order.client_order_id
                )

                self._record_execution()

            return ExecutionResult(

                status=ExecutionStatus.DRY_RUN,

                success=True,

                symbol=order.symbol,

                client_order_id=(
                    order.client_order_id
                ),

                requested_quantity=(
                    order.quantity
                ),

                executed_quantity=(
                    order.quantity
                ),

                requested_price=(
                    order.entry_price
                ),

                executed_price=(
                    order.entry_price
                ),

                stop_loss=(
                    order.stop_loss
                ),

                take_profit=(
                    order.take_profit
                ),

                reason=(
                    "Dry-run execution accepted"
                ),

                metadata={
                    "dry_run": True,
                },
            )

        # =====================================================================
        # BROKER REQUIRED
        # =====================================================================

        if self.broker is None:

            return self._reject(
                order.symbol,
                order.client_order_id,
                "Broker adapter is not configured",
                ExecutionStatus.FAILED,
            )

        # =====================================================================
        # QUOTE CHECK
        # =====================================================================

        quote = self.broker.get_quote(
            order.symbol
        )

        quote_error = (
            self._validate_quote(
                order,
                quote,
            )
        )

        if quote_error:

            return self._reject(
                order.symbol,
                order.client_order_id,
                quote_error,
            )

        # =====================================================================
        # SUBMIT
        # =====================================================================

        try:

            response = (
                self.broker.submit_order(
                    order
                )
            )

        except Exception as exc:

            return self._reject(
                order.symbol,
                order.client_order_id,
                f"Broker submission failed: {exc}",
                ExecutionStatus.FAILED,
            )

        # =====================================================================
        # NORMALIZE RESPONSE
        # =====================================================================

        result = self._normalize_response(
            order,
            response,
        )

        # =====================================================================
        # RECORD SUCCESSFUL SUBMISSION
        # =====================================================================

        if result.success:

            with self._lock:

                self._executed_ids.add(
                    order.client_order_id
                )

                self._record_execution()

        return result

    # =========================================================================
    # ORDER BUILDER
    # =========================================================================

    @staticmethod
    def _order_from_risk(
        risk_result: Any,
    ) -> OrderRequest:

        direction = str(
            getattr(
                risk_result,
                "direction",
                getattr(
                    risk_result,
                    "side",
                    "buy",
                ),
            )
        ).lower()

        if direction in (
            "short",
            "sell",
            "bearish",
        ):

            side = OrderSide.SELL

        else:

            side = OrderSide.BUY

        symbol = str(
            getattr(
                risk_result,
                "symbol",
                "",
            )
        )

        quantity = float(
            getattr(
                risk_result,
                "approved_size",
                0.0,
            )
        )

        entry = getattr(
            risk_result,
            "entry",
            None,
        )

        stop = getattr(
            risk_result,
            "stop_loss",
            None,
        )

        target = getattr(
            risk_result,
            "take_profit",
            None,
        )

        client_id = (
            f"cosmos-"
            f"{symbol}-"
            f"{int(time.time() * 1000)}"
        )

        return OrderRequest(

            symbol=symbol,

            side=side,

            order_type=OrderType.MARKET,

            quantity=quantity,

            entry_price=entry,

            stop_loss=stop,

            take_profit=target,

            client_order_id=client_id,
        )

    # =========================================================================
    # ORDER VALIDATION
    # =========================================================================

    def _validate_order(
        self,
        order: OrderRequest,
    ) -> str | None:

        if not order.symbol:

            return "Order symbol is missing"

        if order.quantity <= 0.0:

            return "Order quantity must be positive"

        if (
            order.quantity
            >
            self.config.max_order_quantity
        ):

            return "Order quantity exceeds execution limit"

        if (
            order.order_type
            ==
            OrderType.MARKET
            and
            not self.config.allow_market_orders
        ):

            return "Market orders are disabled"

        if (
            order.order_type
            ==
            OrderType.LIMIT
            and
            not self.config.allow_limit_orders
        ):

            return "Limit orders are disabled"

        if (
            order.order_type
            ==
            OrderType.STOP
            and
            not self.config.allow_stop_orders
        ):

            return "Stop orders are disabled"

        if (
            self.config.require_stop_loss
            and
            order.stop_loss is None
        ):

            return "Stop-loss is required"

        if order.entry_price is not None:

            if order.entry_price <= 0:

                return "Invalid entry price"

        if order.stop_loss is not None:

            if order.stop_loss <= 0:

                return "Invalid stop-loss"

        if order.take_profit is not None:

            if order.take_profit <= 0:

                return "Invalid take-profit"

        return None

    # =========================================================================
    # QUOTE VALIDATION
    # =========================================================================

    def _validate_quote(
        self,
        order: OrderRequest,
        quote: dict[str, float],
    ) -> str | None:

        if not quote:

            return "Broker quote is unavailable"

        bid = quote.get(
            "bid"
        )

        ask = quote.get(
            "ask"
        )

        if bid is None or ask is None:

            return "Broker quote lacks bid/ask"

        bid = float(bid)

        ask = float(ask)

        if bid <= 0 or ask <= 0:

            return "Invalid broker quote"

        market_price = (
            ask
            if order.side == OrderSide.BUY
            else bid
        )

        if (
            order.entry_price
            is None
        ):

            return None

        deviation = (
            abs(
                market_price
                -
                order.entry_price
            )
            /
            order.entry_price
            *
            100.0
        )

        if (
            deviation
            >
            self.config.max_price_deviation_pct
        ):

            return (
                "Current market price exceeds "
                "maximum allowed deviation"
            )

        return None

    # =========================================================================
    # THROTTLE
    # =========================================================================

    def _execution_allowed(self) -> bool:

        now = time.monotonic()

        with self._lock:

            self._recent_executions = [
                timestamp
                for timestamp
                in self._recent_executions
                if (
                    now - timestamp
                    <=
                    self.config.execution_window_seconds
                )
            ]

            if (
                self._recent_executions
                and
                now
                -
                self._recent_executions[-1]
                <
                self.config.min_execution_interval_seconds
            ):

                return False

            if (
                len(
                    self._recent_executions
                )
                >=
                self.config.max_orders_per_window
            ):

                return False

        return True

    def _record_execution(
        self,
    ) -> None:

        self._recent_executions.append(
            time.monotonic()
        )

    # =========================================================================
    # KILL SWITCH
    # =========================================================================

    def activate_kill_switch(
        self,
    ) -> None:

        self._halted = True

    def reset_kill_switch(
        self,
    ) -> None:

        self._halted = False

    @property
    def halted(
        self,
    ) -> bool:

        return self._halted

    # =========================================================================
    # RESPONSE NORMALIZATION
    # =========================================================================

    @staticmethod
    def _normalize_response(
        order: OrderRequest,
        response: dict[str, Any],
    ) -> ExecutionResult:

        status_raw = str(
            response.get(
                "status",
                "accepted",
            )
        ).lower()

        try:

            status = ExecutionStatus(
                status_raw
            )

        except ValueError:

            status = (
                ExecutionStatus.ACCEPTED
            )

        executed_quantity = float(
            response.get(
                "executed_quantity",
                response.get(
                    "filled_quantity",
                    0.0,
                ),
            )
            or
            0.0
        )

        executed_price = response.get(
            "executed_price"
        )

        if executed_price is not None:

            executed_price = float(
                executed_price
            )

        slippage = 0.0

        if (
            executed_price is not None
            and
            order.entry_price is not None
        ):

            slippage = (
                executed_price
                -
                order.entry_price
            )

        success = (
            status
            in (
                ExecutionStatus.ACCEPTED,
                ExecutionStatus.FILLED,
                ExecutionStatus.PARTIAL,
            )
        )

        return ExecutionResult(

            status=status,

            success=success,

            symbol=order.symbol,

            client_order_id=(
                order.client_order_id
            ),

            broker_order_id=response.get(
                "broker_order_id",
                response.get(
                    "order_id"
                ),
            ),

            requested_quantity=(
                order.quantity
            ),

            executed_quantity=(
                executed_quantity
            ),

            requested_price=(
                order.entry_price
            ),

            executed_price=(
                executed_price
            ),

            stop_loss=(
                order.stop_loss
            ),

            take_profit=(
                order.take_profit
            ),

            slippage=slippage,

            reason=str(
                response.get(
                    "reason",
                    "",
                )
            ),

            warnings=list(
                response.get(
                    "warnings",
                    [],
                )
                or
                []
            ),

            metadata={
                "broker_response": response,
            },
        )

    # =========================================================================
    # CANCEL
    # =========================================================================

    def cancel(
        self,
        broker_order_id: str,
    ) -> bool:

        if self.broker is None:

            return False

        if not broker_order_id:

            return False

        try:

            return bool(
                self.broker.cancel_order(
                    broker_order_id
                )
            )

        except Exception:

            return False

    # =========================================================================
    # CLOSE
    # =========================================================================

    def close_position(
        self,
        symbol: str,
        quantity: float | None = None,
    ) -> dict[str, Any]:

        if self.broker is None:

            return {
                "success": False,
                "reason": (
                    "Broker adapter unavailable"
                ),
            }

        if self._halted:

            return {
                "success": False,
                "reason": (
                    "Execution kill-switch active"
                ),
            }

        try:

            return self.broker.close_position(
                symbol,
                quantity,
            )

        except Exception as exc:

            return {
                "success": False,
                "reason": str(exc),
            }

    # =========================================================================
    # REJECTION
    # =========================================================================

    @staticmethod
    def _reject(
        symbol: str,
        client_order_id: str,
        reason: str,
        status: ExecutionStatus = (
            ExecutionStatus.REJECTED
        ),
    ) -> ExecutionResult:

        return ExecutionResult(

            status=status,

            success=False,

            symbol=symbol,

            client_order_id=client_order_id,

            reason=reason,

            metadata={
                "execution_allowed": False,
            },
        )


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

execution_engine = ExecutionEngine()


# =============================================================================
# PUBLIC API
# =============================================================================

def execute_trade(
    risk_result: Any,
    **kwargs: Any,
) -> ExecutionResult:

    return execution_engine.execute(
        risk_result,
        **kwargs,
    )
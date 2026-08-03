"""
===============================================================================
COSMOS Broker Protocol

Communication protocol between COSMOS Cloud
and Broker Clients.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from enum import Enum

from pydantic import BaseModel
from typing import Optional


class SignalAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"
    MODIFY = "MODIFY"


class SignalStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class TradeSignal(BaseModel):
    """
    Standard communication packet used
    between COSMOS Cloud and Broker Clients.
    """

    signal_id: str

    symbol: str

    action: SignalAction

    volume: float

    stop_loss: Optional[float] = None

    take_profit: Optional[float] = None

    comment: Optional[str] = None

    timestamp: str

    signature: str


class ExecutionReport(BaseModel):
    """
    Broker execution response.
    """

    signal_id: str

    ticket: Optional[int] = None

    status: SignalStatus

    message: Optional[str] = None
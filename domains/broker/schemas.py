"""
===============================================================================
COSMOS Broker Schemas

Pydantic schemas for broker clients.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from pydantic import BaseModel
from pydantic import Field
from typing import Optional


class BrokerClientCreate(BaseModel):
    """
    Register a broker client.
    """

    client_name: str = Field(..., min_length=2, max_length=100)
    broker_name: str = Field(..., min_length=2, max_length=100)
    platform: str = Field(..., min_length=2, max_length=50)
    version: str = Field(..., min_length=1, max_length=20)


class BrokerClientResponse(BaseModel):
    """
    Broker client information.
    """

    id: int
    client_name: str
    broker_name: str
    platform: str
    version: str
    online: bool

    class Config:
        from_attributes = True


class BrokerHeartbeat(BaseModel):
    """
    Heartbeat packet.
    """

    client_id: int
    latency_ms: int
    status: str


class BrokerSignal(BaseModel):
    """
    Standard trading signal.
    """

    symbol: str
    action: str
    volume: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
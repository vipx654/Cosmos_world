"""
===============================================================================
COSMOS Broker Exceptions

Defines broker-specific exceptions.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""


class BrokerError(Exception):
    """Base broker exception."""


class BrokerConnectionError(BrokerError):
    """Unable to connect to broker."""


class BrokerAuthenticationError(BrokerError):
    """Broker authentication failed."""


class OrderRejectedError(BrokerError):
    """Broker rejected the order."""


class InvalidOrderError(BrokerError):
    """Invalid order request."""


class MarketClosedError(BrokerError):
    """Market is currently closed."""


class UnsupportedBrokerError(BrokerError):
    """Broker is not supported."""
"""
===============================================================================
COSMOS Broker Service

Business logic for broker communication.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from domains.broker.models import BrokerClient
from domains.broker.repository import BrokerRepository
from domains.broker.exceptions import BrokerError


class BrokerService:
    """
    Business logic for broker clients.
    """

    def __init__(self, repository: BrokerRepository):
        self.repository = repository

    def register_client(
        self,
        client_name: str,
        broker_name: str,
        platform: str,
        version: str,
    ) -> BrokerClient:

        existing = self.repository.get_by_client_name(client_name)

        if existing:
            raise BrokerError("Broker client already registered.")

        client = BrokerClient(
            client_name=client_name,
            broker_name=broker_name,
            platform=platform,
            version=version,
            online=False,
        )

        return self.repository.create(client)

    def get_client(self, client_id: int):
        return self.repository.get_by_id(client_id)

    def list_clients(self):
        return self.repository.get_all()

    def update_status(
        self,
        client_id: int,
        online: bool,
    ):
        return self.repository.update_status(client_id, online)

    def remove_client(self, client_id: int):
        return self.repository.delete(client_id)
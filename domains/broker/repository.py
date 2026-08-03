"""
===============================================================================
COSMOS Broker Repository

Database operations for broker clients.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from sqlalchemy.orm import Session

from domains.broker.models import BrokerClient


class BrokerRepository:
    """
    Handles database operations for broker clients.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, broker: BrokerClient) -> BrokerClient:
        self.db.add(broker)
        self.db.commit()
        self.db.refresh(broker)
        return broker

    def get_by_id(self, broker_id: int):
        return (
            self.db.query(BrokerClient)
            .filter(BrokerClient.id == broker_id)
            .first()
        )

    def get_by_client_name(self, client_name: str):
        return (
            self.db.query(BrokerClient)
            .filter(BrokerClient.client_name == client_name)
            .first()
        )

    def get_all(self):
        return self.db.query(BrokerClient).all()

    def update_status(
        self,
        broker_id: int,
        online: bool,
    ):
        broker = self.get_by_id(broker_id)

        if broker:
            broker.online = online
            self.db.commit()
            self.db.refresh(broker)

        return broker

    def delete(self, broker_id: int):
        broker = self.get_by_id(broker_id)

        if broker:
            self.db.delete(broker)
            self.db.commit()

        return broker
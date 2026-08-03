"""
===============================================================================
COSMOS Broker Routes

Broker API endpoints.

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from fastapi import APIRouter
from fastapi import HTTPException

from database.session import SessionLocal

from domains.broker.repository import BrokerRepository
from domains.broker.schemas import (
    BrokerClientCreate,
    BrokerClientResponse,
)
from domains.broker.services import BrokerService
from domains.broker.exceptions import BrokerError

router = APIRouter(
    prefix="/broker",
    tags=["Broker"],
)


@router.post(
    "/register",
    response_model=BrokerClientResponse,
)
def register_broker(client: BrokerClientCreate):

    db = SessionLocal()

    try:

        repository = BrokerRepository(db)
        service = BrokerService(repository)

        broker = service.register_client(
            client_name=client.client_name,
            broker_name=client.broker_name,
            platform=client.platform,
            version=client.version,
        )

        return broker

    except BrokerError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    finally:
        db.close()


@router.get(
    "/clients",
    response_model=list[BrokerClientResponse],
)
def list_clients():

    db = SessionLocal()

    try:

        repository = BrokerRepository(db)
        service = BrokerService(repository)

        return service.list_clients()

    finally:
        db.close()


@router.get(
    "/{client_id}",
    response_model=BrokerClientResponse,
)
def get_client(client_id: int):

    db = SessionLocal()

    try:

        repository = BrokerRepository(db)
        service = BrokerService(repository)

        broker = service.get_client(client_id)

        if broker is None:
            raise HTTPException(
                status_code=404,
                detail="Broker client not found.",
            )

        return broker

    finally:
        db.close()
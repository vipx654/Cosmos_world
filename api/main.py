"""
===============================================================================
COSMOS API

FastAPI Application

Author: COSMOS Development Team
License: MIT
===============================================================================
"""

from fastapi import FastAPI

from database.connection import initialize_database
from domains.authentication.routes import router as auth_router
from domains.broker.routes import router as broker_router

app = FastAPI(
    title="COSMOS API",
    version="1.0.0",
    description="COSMOS Trading Operating System Backend",
)


@app.on_event("startup")
def startup():
    initialize_database()


# Authentication
app.include_router(auth_router)

# Broker
app.include_router(broker_router)


@app.get("/")
def root():
    return {
        "message": "COSMOS API Online",
        "status": "running",
    }
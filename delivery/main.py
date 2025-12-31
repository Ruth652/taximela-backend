from fastapi import FastAPI
from delivery.api.routers import health

def create_app() -> FastAPI:
    app = FastAPI(
        title="TaxiMela API",
        version="0.1.0",
        description="Backend service for TaxiMela"
    )

    app.include_router(health.router)

    return app


app = create_app()

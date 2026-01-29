from fastapi import FastAPI
from delivery.api.routers import health
from fastapi.middleware.cors import CORSMiddleware
from delivery.api.routers.route_router import router as route_router
from delivery.api.routers.poi_router import router as poi_router
from delivery.api.routers.geocode_router import router as geocode_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="TaxiMela API",
        version="0.1.0",
        description="Backend service for TaxiMela"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # later restrict to frontend URL
        allow_credentials=True,
        allow_methods=["*"],  # allows OPTIONS, POST, GET
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(route_router)
    app.include_router(poi_router)
    app.include_router(geocode_router)


    return app


app = create_app()

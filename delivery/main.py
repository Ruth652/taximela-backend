from fastapi import FastAPI
from delivery.api.routers import health
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from delivery.api.routers.route_router import router as route_router
from delivery.api.routers.poi_router import router as poi_router
from delivery.api.routers.geocode_router import router as geocode_router
from delivery.api.routers.contribution_router import router as contribution_router
from delivery.api.routers.user_router import router as user_router
from domain import *
from infrastructure.database import Base, engine



def create_app() -> FastAPI:
    app = FastAPI(
        title="TaxiMela API",
        version="0.1.0",
        description="Backend service for TaxiMela"
    )

    security = HTTPBearer()
  
    Base.metadata.create_all(bind=engine)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"], 
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(route_router)
    app.include_router(poi_router)
    app.include_router(geocode_router)
    app.include_router(contribution_router, prefix="/api")
    app.include_router(user_router, prefix="/api")


    return app


app = create_app()

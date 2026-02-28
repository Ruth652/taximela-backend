from fastapi import FastAPI, Request
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from delivery.api.routers import health
from delivery.api.routers.route_router import router as route_router
from delivery.api.routers.poi_router import router as poi_router
from delivery.api.routers.geocode_router import router as geocode_router
from delivery.api.routers.contribution_router import router as contribution_router
from delivery.api.routers.contributions_router import router as contributions_router 
from delivery.api.routers.user_router import router as user_router
from delivery.api.routers.admin_router import router as admin_router  
from delivery.api.routers.admin_user_router import router as admin_user_router

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

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
            errors.append({
                "field": field,
                "error": err["msg"],
                "type": err["type"]
            })

        return JSONResponse(
            status_code=400,
            content={
                "message": "Invalid request data",
                "errors": errors
            }
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "detail": exc.errors(),
                "message": "Invalid request data"
            }
        )

    app.include_router(health.router)
    app.include_router(route_router)
    app.include_router(poi_router)
    app.include_router(geocode_router)

    app.include_router(contribution_router, prefix="/api")
    app.include_router(contributions_router, prefix="/api") 
    app.include_router(user_router, prefix="/api")
    app.include_router(admin_router, prefix="/api") 

    app.include_router(admin_user_router)

    return app


app = create_app()
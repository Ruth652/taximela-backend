from dotenv import load_dotenv
import psycopg2
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from delivery.api.routers import all_routers

from infrastructure.database import Base, engine
import domain

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

    for r in all_routers:
        app.include_router(r["router"], prefix = r["prefix"])
    try:
        psycopg2.connect("postgresql://postgres:TaxiMela123@db.cldxkswkintnwktfjwrf.supabase.co:5432/postgres")
        print("OK")
    except Exception as e:
        print("ERR", e)

    return app

app = create_app()
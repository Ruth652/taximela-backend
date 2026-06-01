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
from infrastructure.scheduler_service import start_scheduler
from usecases.rebuild_graph_usecase import RebuildGraphUseCase
from infrastructure.database import get_db
from infrastructure.otp_database import get_otp_db

from domain.stops_model import Stops
from domain.stop_times_model import StopTimes
from domain.transfers_model import Transfer
from domain.trips_model import Trips    
from domain.route_otp_model import Routes
from domain.shape_model import Shapes
from domain.calendar_model import Calendar
from domain.notification_model import Notification
from domain.subscription_model import BusinessSubscription
from domain.auth_handoff_model import AuthHandoffToken

def scheduled_rebuild():
    print("Running scheduled rebuild...")
    db = next(get_db())
    otp_db = next(get_otp_db())
    usecase = RebuildGraphUseCase(db=db, otp_db=otp_db, user_id="system")
    usecase.execute()


def expire_subscriptions():
    print("Checking for expired subscriptions...")
    from repository.subscription_repository import SubscriptionRepository
    db = next(get_db())
    try:
        count = SubscriptionRepository(db).expire_stale_subscriptions()
        if count:
            print(f"Expired {count} subscription(s)")
    finally:
        db.close()

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
        
    @app.on_event("startup")
    def startup_event():
        start_scheduler(scheduled_rebuild, expire_subscriptions)
    try:
        psycopg2.connect("postgresql://postgres:TaxiMela123@db.cldxkswkintnwktfjwrf.supabase.co:5432/postgres")
        print("OK")
    except Exception as e:
        print("ERR", e)
        

    return app

app = create_app()
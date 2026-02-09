# main.py
from fastapi import FastAPI
from delivery.api.routers.admin_router import router as admin_router
from delivery.api.routers.contributions_router import router as contributions_router

app = FastAPI()

app.include_router(contributions_router)
app.include_router(admin_router)
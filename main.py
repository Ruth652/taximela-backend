# main.py

from fastapi import FastAPI
from delivery.api.routers.contribution_router import router as contribution_router
from delivery.api.routers.admin_router import router as admin_router
from delivery.api.routers.contributions_router import router as contributions_router
from delivery.api.routers.route_router import router as route_router
from delivery.api.routers.user_router import router as user_router

app = FastAPI()

app.include_router(contributions_router)
app.include_router(admin_router)
app.include_router(route_router)
app.include_router(contribution_router)
app.include_router(user_router)
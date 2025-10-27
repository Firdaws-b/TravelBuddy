import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI
from config.settings import settings
from src.routers import hotel_router, auth_router, user_router, destination_router
app = FastAPI(title="TravelBuddy API", version="1.0.0")
# Include router with base prefix (e.g., /api/v1)
app.include_router(hotel_router.router, prefix=settings.BASE_ROUTE)
app.include_router(user_router.router, prefix=settings.BASE_ROUTE)
app.include_router(auth_router.router, prefix=settings.BASE_ROUTE)
app.include_router(destination_router.router, prefix=settings.BASE_ROUTE)

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from fastapi import FastAPI
from .routers import hotel_routes, flights_router

app = FastAPI(title="TravelBuddy API", version="1.0.0")


# Include router with base prefix (e.g., /api/v1)
app.include_router(hotel_routes.router, prefix=settings.BASE_ROUTE)
app.include_router(flights_router.router, prefix=settings.BASE_ROUTE)

for route in app.routes:
    print(route.path)

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
from fastapi import FastAPI
from src.config import settings
from src.routes import hotel_routes

app = FastAPI(title="TravelBuddy API", version="1.0.0")


# Include router with base prefix (e.g., /api/v1)
app.include_router(hotel_routes.router, prefix=settings.BASE_ROUTE)

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
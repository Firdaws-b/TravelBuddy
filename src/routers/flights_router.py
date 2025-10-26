

from fastapi import APIRouter, Depends, Query
from src.schemas.flights_schemas import FlightSearchRequest, FlightSearchResponse
from src.services.flights_service import FlightsService


router = APIRouter(prefix="/flights", tags=["flights"])
service = FlightsService()
# Search for flights based on user
@router.get("/", response_model=list[FlightSearchResponse])
async def get_flights(query: str = Query(..., description="Enter your flight search query")):
    print("HELLO FROM FLIGHTS ROUTER")
    return await service.search_flights(query)




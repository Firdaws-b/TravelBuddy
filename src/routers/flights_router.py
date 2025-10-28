

from fastapi import APIRouter, Query

from src.models.flights_model import FlightsListSearchResponse, FlightInfoResponse
from src.services.flights_service import FlightsService


router = APIRouter(prefix="/flights", tags=["flights"])
service = FlightsService()

# 1st API Call: Search for flights based on user
@router.get("/", response_model=list[FlightsListSearchResponse])
async def get_flights(query: str = Query(..., description="Enter your flight search query")):
    print("HELLO FROM FLIGHT LIST  ROUTER")
    flights = await service.search_flights_list(query)
    # Save the flights list in DB
    await service.save_flights_list(query,flights)
    return flights
# 2nd API Call:
@router.get("/flight_number", response_model = FlightInfoResponse)
async def get_flight_info(query: str = Query(..., description="Enter your flight search query about info")):
    print("HELLO FROM FLIGHT INFO")
    return await service.search_flight_info(query)






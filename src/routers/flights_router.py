from fastapi import APIRouter, Query, Depends

from config.databse import users_collection
from src.models.flights_model import FlightsListSearchResponse, FlightInfoResponse, BookFlightResponse, \
    DeleteFlightResponse
from src.services.user_service import get_current_user
from src.services.flights_service import FlightsService
router = APIRouter(prefix="/flights", tags=["flights"])
service = FlightsService()

# 1st API Call: Search for flights based on user
@router.get("/", response_model=list[FlightsListSearchResponse])
async def get_flights(
        query: str = Query(..., description="Enter your flight search query"),
        # current_user: dict = Depends(get_current_user)
):
    print("HELLO FROM FLIGHT LIST  ROUTER")
    flights = await service.search_flights_list(query)
    # Save the flights list in DB
    # await service.save_flights_list(query,flights, user_id=current_user["_id"])
    await service.save_flights_list(query, flights, user_id=None)
    return flights
# 2nd API Call:
@router.get("/flight_number", response_model = FlightInfoResponse)
async def get_flight_info(query: str = Query(..., description="Enter your flight search query about info")):
    print("HELLO FROM FLIGHT INFO")
    return await service.search_flight_info(query)
@router.post("/flight_number)", response_model=BookFlightResponse)
async def book_flight(query: str = Query(..., description="Enter your the flight you want to book"),
                      user_email: str=Query(..., description="Enter your email address please") ,
                      current_user: dict = Depends(get_current_user)):


    print("HELLO FROM book_flight endpoint")
    if current_user["email"] == user_email:
        return await service.book_flight(query, user_email=user_email)
    else:
        return {"error": "Unauthorized: Email does not match the logged-in user"}

# cancel flight
@router.delete("/booking_id", response_model=DeleteFlightResponse)
async def cancel_flight(query: str = Query(..., description="Enter your booking reference to cancel the flight"),
                        current_user: dict = Depends(get_current_user), user_email: str=Query(..., description="Enter your email address please") ):
    print("HELLO FROM cancel_flight endpoint")
    return await service.cancel_flight(query, user_email=user_email)









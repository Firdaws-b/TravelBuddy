from fastapi import APIRouter, Query, Depends, Body

from config.databse import users_collection
from src.models.flights_model import FlightsListSearchResponse, FlightInfoResponse, BookFlightResponse, \
    DeleteFlightResponse, UserBookedFlightsResponse, FlightsListSearchRequest, FlightInfoRequest, BookFlightRequest, \
    DeleteFlightRequest
from src.services.user_service import get_current_user
from src.services.flights_service import FlightsService
router = APIRouter(prefix="/flights", tags=["flights"])
service = FlightsService()

# 1st API Call: Search for flights based on user
@router.post("/", response_model=list[FlightsListSearchResponse])
async def search_flights(
        flight_input: FlightsListSearchRequest = Body(...),
        current_user: dict = Depends(get_current_user)
):
    print("HELLO FROM FLIGHT LIST  ROUTER")
    flights = await service.search_flights_list(flight_input)
    # Save the flights list in DB
    # await service.save_flights_list(query,flights, user_id=current_user["_id"])
    await service.save_flights_list( flights=flights, user_id=current_user["_id"])
    return flights
# 2nd API Call: Get flight info based on flight number
@router.post("/flight_number", response_model = FlightInfoResponse)
async def get_flight_info(flight_input: FlightInfoRequest = Body()):
    print("HELLO FROM FLIGHT INFO")
    return await service.search_flight_info(flight_input)
# 3rd API Call book flight
@router.post("/flight_number)", response_model=BookFlightResponse)
async def book_flight(flight_input: BookFlightRequest = Body(...),
                      current_user: dict = Depends(get_current_user)):
    print("HELLO FROM book_flight endpoint")
    if current_user["email"] == flight_input.user_email:
        return await service.book_flight(flight_input)
    else:
        return {"error": "Unauthorized: Email does not match the logged-in user"}

# 4th API call: cancel flight
@router.delete("/booking_id", response_model=DeleteFlightResponse)
async def cancel_flight(cancel_flight_input: DeleteFlightRequest = Body(...),
                        current_user: dict = Depends(get_current_user)):

    print("HELLO FROM cancel_flight endpoint")
    return await service.cancel_flight(cancel_flight_input, current_user)

# 5th API Call: get user's booked flights history
@router.get("/booked_flights_history", response_model=UserBookedFlightsResponse)
async def get_booking_history(
        current_user: dict = Depends(get_current_user)
):
    print("HELLO FROM BOOKING HISTORY endpoint")
    bookings = await service.get_user_booked_flights(current_user=current_user)
    return bookings






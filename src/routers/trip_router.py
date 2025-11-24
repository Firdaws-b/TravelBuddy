from fastapi import APIRouter
from src.models.trip_model import PlannedTripModel, PlanATrip, TripSummaryModel, UpdateTripModel, ItineraryDayModel
from src.models.user_model import UserFeedback, UserProfile
from src.services.trip_service import plan_trip_service, get_trips_service, get_planned_trip_service, update_trip_service, cancel_trip_service, regenerate_itinerary_service, get_itinerary_service
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.services.user_service import get_current_user

router = APIRouter(prefix="/trips", tags=["trips"])

# plan a trip
@router.post("/", response_model=PlannedTripModel)
async def create_trip(trip:PlanATrip, current_user: dict = Depends(get_current_user)):
    print("Current user email is ", current_user["email"])
    planned_trip = await plan_trip_service(trip.destination,trip.budget,trip.duration,
                                           trip.number_of_travelers,current_user["email"], trip.date)
    return planned_trip

# Return all trips of the authenticated user
@router.get("/", response_model=list[TripSummaryModel])
def get_trips(current_user: dict = Depends(get_current_user)):
    return get_trips_service(current_user["email"])

# Return details of a specific trip
@router.get("/{trip_id}", response_model=PlannedTripModel)
def get_planned_trip(trip_id: str, current_user: dict = Depends(get_current_user)):
    return get_planned_trip_service(trip_id, current_user["email"])

# Full update of a specific trip
@router.put("/{trip_id}", response_model=PlannedTripModel)
async def update_trip(trip_id: str, trip:UpdateTripModel, current_user: dict = Depends(get_current_user)):
    return await update_trip_service(trip_id, trip.duration,trip.budget,trip.number_of_travelers, trip.planned_date_time, current_user["email"])



@router.delete("/{trip_id}", response_model=TripSummaryModel)
def cancel_trip(trip_id: str,current_user: dict = Depends(get_current_user)):
    return cancel_trip_service(trip_id, current_user["email"])

# retrieve the itinerary of a specific trip
@router.get("/{trip_id}/itinerary", response_model=list[ItineraryDayModel])
def get_itinerary(trip_id: str, current_user: dict = Depends(get_current_user)):
    return get_itinerary_service(trip_id, current_user["email"])


@router.post("/{trip_id}/itinerary", response_model=list[ItineraryDayModel])
async def regenerate_itinerary(trip_id: str, user_feedback: UserFeedback, current_user: dict = Depends(get_current_user)):
    return await regenerate_itinerary_service(trip_id, user_feedback.user_feedback, current_user["email"])


# TODO EXPORT THE GENERATED TRIP INTO A PDF FILE WITH ALL TRIP DETAILS




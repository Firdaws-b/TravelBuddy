# TODO Implement trip_router
from fastapi import APIRouter, Depends
from src.models.trip_model import PlannedTripModel, PlanATrip, TripSummaryModel, UpdateTripModel, ItineraryDayModel
from src.services.trip_service import plan_trip_service, get_trips_service, get_planned_trip_service, update_trip_service, cancel_trip_service, regenerate_itinerary_service, get_itinerary_service

router = APIRouter(prefix="/trips", tags=["trips"])

# plan a trip
@router.post("/", response_model=PlannedTripModel)
async def create_trip(trip:PlanATrip):
    planned_trip = await plan_trip_service(trip.destination,trip.budget,trip.duration,trip.number_of_travelers,trip.user_email_address, trip.date)
    return {"Planned Trip": planned_trip}

# Return all trips
@router.get("/", response_model=list[TripSummaryModel])
def get_trips():
    return get_trips_service()

# Return details of a specific trip
@router.get("/{trip_id}", response_model=PlannedTripModel)
def get_planned_trip(trip_id: str):
    return get_planned_trip_service(trip_id)

# Full update of a specific trip
@router.put("/{trip_id}", response_model=PlannedTripModel)
async def update_trip(trip_id: str, trip:UpdateTripModel):
    return await update_trip_service(trip_id, trip.duration,trip.budget,trip.number_of_travelers, trip.planned_date_time)



@router.delete("/{trip_id}", response_model=ItineraryDayModel)
def cancel_trip(trip_id: str):
    return cancel_trip_service(trip_id)

# retrieve the itinerary of a specific trip
@router.get("/{trip_id}/itinerary", response_model=list[ItineraryDayModel])
def get_itinerary(trip_id: str):
    return get_itinerary_service(trip_id)


@router.post("/{trip_id}/itinerary", response_model=list[ItineraryDayModel])
async def regenerate_itinerary(trip_id: str):
    return await regenerate_itinerary_service(trip_id)







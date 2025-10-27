# TODO Implement trip_router
from fastapi import APIRouter, Depends
from src.models.trip_model import PlannedTripModel, PlanATrip
from src.services.trip_service import plan_trip_service

router = APIRouter(prefix="/trips", tags=["trips"])

# plan a trip
@router.post("/")
async def create_trip(trip:PlanATrip):
    planned_trip = await plan_trip_service(trip.destination,trip.budget,trip.duration,trip.number_of_travelers,trip.user_id)
    return {"Planned Trip": planned_trip}

# @router.get("/")
# def get_trips():
#
# @router.get("/{trip_id}")
# def get_trip(trip_id: int):
#
# @router.put("/{trip_id}")
# def update_trip(trip_id: int, trip: PlannedTripModel):
#
# @router.delete("/{trip_id}")
# def delete_trip(trip_id: int):
#
# @router.get("/{trip_id}/itinerary")
# def get_itinerary(trip_id: int):
#
# @router.post("/{trip_id}/itinerary")
# def regenerate_itinerary(trip_id: int, itinerary: PlannedTripModel):




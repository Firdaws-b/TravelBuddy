from fastapi import APIRouter, Query
from fastapi import Depends
from src.models.destination_model import Destination
from src.models.recommendation_request import RecommendationRequest
from src.models.trip_model import PlannedTripModel, PlanATrip
from src.services.orchestrator import get_recommendations, plan_trip #, search_flights_service, search_hotels_service
from src.services.user_service import get_current_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
router = APIRouter(prefix="/orchestrator", tags=["Orchestrator"])
security = HTTPBearer()
# Orchestrator sends request to destination service with user query
@router.post("/recommended_destinations")
async def recommend_destination(query: str = Query(..., description="Describe what kind of destination you want"),
    limit: int = Query(5, ge=1, le=20),
    user_id: str = Query(None, description="Optional user ID for personalized results")):
    return await get_recommendations(query,limit,user_id)
#
# Orchestrator sends request to create a trip (Trips Service)
@router.post("/planned_trip")
async def plan_trip_endpoint(trip: PlanATrip, credentials: HTTPAuthorizationCredentials = Depends(security), current_user: dict = Depends(get_current_user)):
    user_token = credentials.credentials
    return await plan_trip(trip,current_user["email"], user_token=user_token)

    # return await plan_trip(destination, current_user["email"])
#
# # Orchestrator sends request to search for flights (Flight Service)
# @router.post("/flights_results")
# async def search_flights():
#     return await search_flights_service()
#
# # Orchestrator sends requests to search for hotels (Hotels Service)
# @router.get("/hotels_results")
# async def hotels_results():
#     return await search_hotels_service()
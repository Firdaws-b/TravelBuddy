from fastapi import APIRouter, Query
from fastapi import Depends
from src.models.destination_model import Destination
from src.models.flights_model import FlightsListSearchRequest
from src.models.recommendation_request import RecommendationRequest
from src.models.trip_model import PlannedTripModel, PlanATrip
from src.models.vacation_model import VacationModel
from src.services.vacation import get_recommendations, plan_vacation_service
from src.services.user_service import get_current_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
router = APIRouter(prefix="/vacation", tags=["Vacation"])
security = HTTPBearer()
# Orchestrator sends request to destination service with user query
@router.post("/recommended_destinations")
async def recommend_destination(query: str = Query(..., description="Describe what kind of destination you want"),
    limit: int = Query(5, ge=1, le=20),
    user_id: str = Query(None, description="Optional user ID for personalized results")):
    return await get_recommendations(query,limit,user_id)

#Plan vacation
@router.post("/planned_vacation")
async def plan_vacation_endpoint(vacation_model:VacationModel,credentials: HTTPAuthorizationCredentials = Depends(security), current_user: dict = Depends(get_current_user)):
    user_token = credentials.credentials
    return await plan_vacation_service(vacation_model.user_request,current_user["email"],user_token=user_token)


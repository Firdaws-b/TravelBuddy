from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.services.destination_service import recommend_destinations, get_user_by_id, create_recommendation, get_past_recommendations, regenerate_recommendation, delete_recommendation
from src.services.user_service import get_current_user


from src.services.destination_service import (
    recommend_destinations,
    get_user_by_id,
    create_recommendation,
    get_past_recommendations,
    regenerate_recommendation,
    delete_recommendation
)

from src.services.user_service import get_current_user

router = APIRouter(tags=["destinations"])
security = HTTPBearer()


# Public: simple recommendation (no DB writes)
@router.get("/destinations/recommendation")
def recommend_destinations_api(
    query: str = Query(..., description="Describe what kind of destination you want"),
    limit: int = Query(5, ge=1, le=20),
    user_id: str = Query(None, description="Optional user ID for personalized results")
):
    try:
        user_prefs = {}
        if user_id:
            user = get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user_prefs = user.get("preferences", {})

        results = recommend_destinations(query, limit, user_prefs)
        return {"query": query, "results": results}
    except Exception as e:
        print("Exception is ****** ", e)
        raise HTTPException(status_code=500, detail=str(e))


# Protected: create + store recommendation
@router.post("/destinations/recommendations")
def create_recommendation_api(
    user_id: str = Query(...),
    query: str = Query(...),
    limit: int = Query(5, ge=1, le=20),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict = Depends(get_current_user)
):
    try:
        return create_recommendation(user_id, query, limit)
    except Exception as e:
        print("Exception is ****** ", e)
        raise HTTPException(status_code=500, detail=str(e))


# Protected: get past recommendations
@router.get("/destinations/recommendations/{user_id}")
def get_user_recommendations_api(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict = Depends(get_current_user)
):
    try:
        return get_past_recommendations(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Protected: regenerate recommendation
@router.put("/destinations/recommendations/{rec_id}/regenerate")
def regenerate_recommendation_api(
    rec_id: str,
    new_query: str = Query(...),
    limit: int = Query(5, ge=1, le=20),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict = Depends(get_current_user)
):
    try:
        return regenerate_recommendation(rec_id, new_query, limit)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Protected: delete recommendation
@router.delete("/destinations/recommendations/{rec_id}")
def delete_recommendation_api(
    rec_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict = Depends(get_current_user)
):
    try:
        success = delete_recommendation(rec_id)
        if not success:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        return {"message": "Recommendation deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

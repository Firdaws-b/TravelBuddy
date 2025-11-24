from fastapi import APIRouter, HTTPException, Query
from src.services.destination_service import recommend_destinations, get_user_by_id

router = APIRouter(tags=["destinations"])

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
        raise HTTPException(status_code=500, detail=str(e))

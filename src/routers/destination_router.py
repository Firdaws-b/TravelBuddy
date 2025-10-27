from fastapi import APIRouter, HTTPException, Query
from typing import List
from src.models.destination_model import Destination
from src.services.destination_service import get_all_destinations, recommend_destinations

router = APIRouter(prefix="/destinations", tags=["Destinations"])

@router.get("/", response_model=List[Destination])
def list_destinations(limit: int = Query(50, ge=1, le=200)):
    try:
        destinations = get_all_destinations(limit)
        return destinations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend", response_model=List[Destination])
def recommend(
    query: str = Query(..., description="Describe what kind of destination you want (e.g., 'warm beaches with nightlife')"),
    limit: int = Query(5, ge=1, le=20)
):
    
    try:
        results = recommend_destinations(query, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

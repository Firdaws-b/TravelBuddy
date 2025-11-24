from pydantic import BaseModel
from typing import Optional

class RecommendationRequest(BaseModel):
    user_id: Optional[str] = None
    query: str
    preferences: Optional[dict] = None
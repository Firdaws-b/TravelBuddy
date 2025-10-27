from pydantic import BaseModel, Field
from typing import List, Optional

class Destination(BaseModel):
    id: str = Field(default=None, alias="_id")
    name: str
    country: str
    description: Optional[str] = None
    tags: List[str] = []
    best_time_to_visit: Optional[str] = None
    average_cost: Optional[float] = None

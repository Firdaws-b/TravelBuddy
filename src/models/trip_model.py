# Used to define Pydantic models, by defining the structure
# and validation rules for data
# Trip
import json
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class ItineraryDayModel(BaseModel):
    planned_day : datetime
    activities: List[str] = Field(default_factory=list)
    title: str = Field(default_factory=str)

# Plan A Trip Response
class PlannedTripModel(BaseModel):
    user_id: str = Field(default_factory=str)  # each trip has a user assigned to it
    trip_id: str = Field(default_factory=str)
    planned_date_time: datetime = Field(default_factory=datetime.now)
    destination: str
    cost_per_traveler: float
    duration: float
    number_of_travelers: int
    list_activities: List[str] = Field(default_factory=list)
    overall_cost: float
    generated_itinerary: Optional[List[ItineraryDayModel]] = None

    def calculate_overall_cost(self) -> float:
        self.overall_cost = self.number_of_travelers + self.overall_cost_per_traveler
        return self.overall_cost_per_traveler


# Plan a trip Request
class PlanATrip(BaseModel):
    destination: str
    budget: float
    duration : float
    number_of_travelers: int
    user_id: str = Field(default_factory=str)




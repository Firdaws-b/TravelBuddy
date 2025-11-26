# Used to define Pydantic models, by defining the structure
# and validation rules for data
# Trip
import json
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class ItineraryDayModel(BaseModel):
    day : int
    activities: List[str] = Field(default_factory=list)

# Plan A Trip Response
class PlannedTripModel(BaseModel):
    user_email_address: str = Field(default_factory=str)  # each trip has a user assigned to it
    trip_id: str = Field(default_factory=str)
    planned_date_time: datetime = Field(default_factory=datetime.now)
    destination: str
    cost_per_traveler: Optional[float] = Field(default=None)
    duration: float
    number_of_travelers: Optional[int] = Field(default=None)
    overall_cost: float
    generated_itinerary: Optional[List[ItineraryDayModel]] = None

    def calculate_overall_cost(self) -> float:
        self.overall_cost = self.number_of_travelers + self.overall_cost_per_traveler
        return self.overall_cost_per_traveler

    def generate_trip_id(self):
        date = self.planned_date_time.strftime("%y%m%d")
        unique = str(uuid.uuid4())[:6].upper()
        self.trip_id = f"{self.destination[:3].upper()}-{date}-{unique}"
        return self.trip_id




# Plan a trip Request
class PlanATrip(BaseModel):
    destination: str
    budget: float
    duration : float
    number_of_travelers: int
    date: datetime


class TripSummaryModel(BaseModel):
    trip_id: str = Field(default_factory=str)
    destination: str
    duration: float
    overall_cost: float

class UpdateTripModel(BaseModel):
    duration: Optional[int] = None
    budget: Optional[float] = None           # user update
    overall_cost: Optional[float] = None     # internal update
    number_of_travelers: Optional[int] = None
    planned_date_time: Optional[datetime] = None




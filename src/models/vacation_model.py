from typing import Optional

from pydantic import BaseModel, Field

from src.models.flights_model import FlightsListSearchRequest
from src.models.trip_model import PlanATrip


# class VacationModel(BaseModel):
#
#     trip: PlanATrip
#     flight: Optional[FlightsListSearchRequest]
#     hotel_query: str

class VacationModel(BaseModel):
    user_request: str

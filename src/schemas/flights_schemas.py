from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# Request schema for searching available flights
class FlightSearchRequest(BaseModel):
    departure_airport: str
    arrival_airport: str
    departure_date: date  # Format: YYYY-MM-DD
    cabin_class: Optional[str] = "Economy"
    currency: Optional[str] = "CAD"
    adults: Optional[int] = 1
    children: Optional[int] = 0
    infants: Optional[int] = 0

# Response schema for flight search results
class FlightSearchResponse(BaseModel):
    flight_number: str
    airline: str
    departure_airport: str  # ISO 8601 format
    arrival_airport: str    # ISO 8601 format
    departure_time: datetime
    arrival_time: datetime
    duration: str
    price: str



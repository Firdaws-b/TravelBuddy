from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# Search Flights List

# Request schema for searching available flights
class FlightsListSearchRequest(BaseModel):
    departure_airport: str
    arrival_airport: str
    departure_date: str  # Format: YYYY-MM-DD
    cabin_class: Optional[str] = "Economy"
    currency: Optional[str] = "CAD"
    adults: Optional[int] = 1
    children: Optional[int] = 0
    infants: Optional[int] = 0

# Response schema for flights list search results
class FlightsListSearchResponse(BaseModel):
    flight_number: str
    airline: str
    departure_airport: str  # ISO 8601 format
    arrival_airport: str    # ISO 8601 format
    departure_time: str
    arrival_time: str
    duration: str
    price: str

# Flight Info
# Request schema for flight information
class FlightInfoRequest(BaseModel):
    flight_number: str
    airline: str
    departure_date: str
# Response schema for flight information
class FlightInfoResponse(BaseModel):
    flight_number:str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: str
    status: str
    actual_departure: Optional[str] = None
    actual_arrival: Optional[str] = None
    terminal_departure: Optional[str] = None
    terminal_arrival: Optional[str] = None
    gate_departure: Optional[str] = None
    gate_arrival: Optional[str] = None
    scheduled_departure: Optional[str] = None
    scheduled_arrival: Optional[str] = None


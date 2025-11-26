import uuid

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

from src.models.user_model import UserProfile


# Declare Base Models
class Flight(BaseModel):
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    carrier_code: str
    flight_number: str
    duration: Optional[str]

class Itinerary(BaseModel):
    segments: List[Flight]

class Price(BaseModel):
    currency: str
    total: str
    grand_total: str

# Search Flights List

# Request model for searching available flights
class FlightsListSearchRequest(BaseModel):
    departure_airport: str
    arrival_airport: str
    departure_date: str  # Format: YYYY-MM-DD
    cabin_class: Optional[str] = "Economy"
    currency: Optional[str] = "CAD"
    adults: Optional[int] = 1
    children: Optional[int] = 0
    infants: Optional[int] = 0
    airline: Optional[str] = None

# Response model for flights list search results
class FlightsListSearchResponse(BaseModel):
    flight_number: str
    airline: str
    departure_airport: str  # ISO 8601 format
    arrival_airport: str    # ISO 8601 format
    departure_time: str
    arrival_time: str
    departure_date: str
    duration: str
    price: str

# Flight Info
# Request model for flight information
class FlightInfoRequest(BaseModel):
    flight_number: str
    airline: str
    departure_date: str
# Response model for flight information
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



# Request model for Book a flight
class BookFlightRequest(BaseModel):
    user_email: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_date: str
    cabin_class: str
    traveler_type: str
    currency: str
    adults: int
    children: int
    infants: int


# Response model for Book a flight
class BookFlightResponse(BaseModel):
    booking_id :str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_status : Optional[str] = "Pending"
    itineraries : List[Itinerary]
    price: Price

# Request model for Cancel a flight
class DeleteFlightRequest(BaseModel):
    booking_id: str
    user: Optional[UserProfile] = Field(None, description="User profile")
# Response model for Cancel a flight
class DeleteFlightResponse(BaseModel):
    booking_id : str
    booking_status : str = "Cancelled"
    refund_amount : Optional[Price] = None

class UserBookedFlightsResponse(BaseModel):
    booked_flights: List[BookFlightResponse]



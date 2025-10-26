
import os
from datetime import datetime
from multiprocessing.reduction import send_handle

from dotenv import load_dotenv
from src.schemas.flights_schemas import FlightSearchRequest, FlightSearchResponse
from amadeus import Client, ResponseError
import httpx

from src.utils.parser import parse_input

load_dotenv()
amadeus_client_id = os.getenv("AMADEUS_CLIENT_ID")
amadeus_client_secret = os.getenv("AMADEUS_CLIENT_SECRET")



class FlightsService:
    def __init__(self):
        self.amadeus = Client(
        client_id = amadeus_client_id,
        client_secret = amadeus_client_secret)

    async def search_flights(self, query: str) -> list[FlightSearchResponse]:
        # Define parameters for the API request
        # Use hugging face model to parse user query into structured data
        flight_request : FlightSearchRequest = parse_input(query)
        # Make the API request to Amadeus
        print("Sending request to Amadeus API with parameters:")
        print(  {"originLocationCode": flight_request.departure_airport,
                "destinationLocationCode" : flight_request.arrival_airport,
                "departureDate": str(flight_request.departure_date),
                "adults": flight_request.adults,
                "children": flight_request.children,
                "infants": flight_request.infants,
                "travelClass": flight_request.cabin_class,
                "currencyCode": flight_request.currency,})
        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode = flight_request.departure_airport,
                destinationLocationCode = flight_request.arrival_airport,
                departureDate = str(flight_request.departure_date),
                adults = flight_request.adults,
                children = flight_request.children,
                infants = flight_request.infants,
                travelClass = flight_request.cabin_class,
                currencyCode = flight_request.currency,
                max = 5,
            )
            flight_data = response.data
        except ResponseError as error:
            print("Error in the Amadeus API request:", error)
            return []

        # Define the response parsing logic
        flights = []
        for item in flight_data:
            # Extract relevant flight details from the response
            segment = item["itineraries"][0]["segments"][0]
            flight = FlightSearchResponse(
                flight_number= segment["carrierCode"] + segment["number"],
                airline=segment["carrierCode"],
                departure_airport=segment["departure"]["iataCode"],
                arrival_airport=segment["arrival"]["iataCode"],
                departure_time=datetime.fromisoformat(segment["departure"]["at"]),
                arrival_time=datetime.fromisoformat(segment["arrival"]["at"]),
                duration=item["itineraries"][0]["duration"],
                price=item["price"]["total"],
                cabin_class = flight_request.cabin_class
            )
            flights.append(flight)
        return flights
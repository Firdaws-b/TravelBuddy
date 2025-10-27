import os
from datetime import datetime
from multiprocessing.reduction import send_handle
from typing import Union

from dotenv import load_dotenv
from mpmath.libmp import to_int
from word2number import w2n

from src.schemas.flights_schemas import (
    FlightsListSearchRequest,
    FlightsListSearchResponse,
    FlightInfoResponse,
    FlightInfoRequest,
)
from amadeus import Client, ResponseError
import httpx

from src.utils.parser import FlightQueryParser

load_dotenv()
amadeus_client_id = os.getenv("AMADEUS_CLIENT_ID")
amadeus_client_secret = os.getenv("AMADEUS_CLIENT_SECRET")


class FlightsService:
    def __init__(self):
        self.amadeus = Client(
            client_id=amadeus_client_id,
            client_secret=amadeus_client_secret,
        )
        self.parser = FlightQueryParser()

    async def search_flights_list(self, query: str) -> list[FlightsListSearchResponse]:
        # Define parameters for the API request
        flight_request: FlightsListSearchRequest = self.parser.parse_query_flights_list(query)

        # Make the API request to Amadeus
        print("Sending request to Amadeus API with parameters:")
        print({
            "originLocationCode": flight_request.departure_airport,
            "destinationLocationCode": flight_request.arrival_airport,
            "departureDate": str(flight_request.departure_date),
            "adults": flight_request.adults,
            "children": flight_request.children,
            "infants": flight_request.infants,
            "travelClass": flight_request.cabin_class,
            "currencyCode": flight_request.currency,
        })

        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=flight_request.departure_airport,
                destinationLocationCode=flight_request.arrival_airport,
                departureDate=str(flight_request.departure_date),
                adults=flight_request.adults,
                children=flight_request.children,
                infants=flight_request.infants,
                travelClass=flight_request.cabin_class,
                currencyCode=flight_request.currency,
                max=5,
            )
            flight_data = response.data
        except ResponseError as error:
            print("Error in the Amadeus API request:", error)
            return []

        # Define the response parsing logic
        flights = []
        for item in flight_data:
            itineraries = item["itineraries"]
            for itinerary in itineraries:
                segment_info = []
                total_duration = itinerary.get("duration", "")
                for segment in itinerary.get("segments"):
                    segment_info.append({
                        "flight_number": segment["carrierCode"] + segment["number"],
                        "airline": segment["carrierCode"],
                        "departure_airport": segment["departure"]["iataCode"],
                        "arrival_airport": segment["arrival"]["iataCode"],
                        "departure_time": segment["departure"]["at"],
                        "arrival_time": segment["arrival"]["at"],
                    })

                flight = FlightsListSearchResponse(
                    flight_number=" -> ".join([s["flight_number"] for s in segment_info]),
                    airline=", ".join([s["airline"] for s in segment_info]),
                    departure_airport=segment_info[0]["departure_airport"],
                    arrival_airport=segment_info[-1]["arrival_airport"],
                    departure_time=segment_info[0]["departure_time"],
                    arrival_time=segment_info[-1]["arrival_time"],
                    duration=total_duration,
                    price=item["price"]["total"],
                    cabin_class=flight_request.cabin_class,
                )
                flights.append(flight)
        return flights

    async def search_flight_info(self, query: str) -> Union[FlightInfoResponse, dict]:
        # Define parameters used as inputs for our search query
        flight_info_request: FlightInfoRequest = self.parser.parse_query_flight_info(query)

        # Make the API call to Amadeus
        print("Sending request to Amadeus API with parameters:")
        print({
            "carrierCode": flight_info_request.airline,
            "flightNumber": flight_info_request.flight_number,
            "scheduledDepartureDate": flight_info_request.departure_date,

        })
        try:
            response = self.amadeus.flight.status.get(
                carrierCode=flight_info_request.airline,
                flightNumber=flight_info_request.flight_number,
                scheduledDepartureDate=flight_info_request.departure_date,
            )
            flight_data = response.data
        except ResponseError as error:
            print("Error in the Amadeus API request:", error)
        flight_info = flight_data[0]

        flight = FlightInfoResponse(
            flight_number=flight_info.get("flightNumber"),
            airline=flight_info.get("carrier", {}).get("name", flight_info_request.airline),
            status=flight_info.get("status"),
            departure_airport=flight_info.get("departure", {}).get("iataCode"),
            arrival_airport=flight_info.get("arrival", {}).get("iataCode"),
            scheduled_departure=flight_info.get("departure", {}).get("scheduledTime"),
            scheduled_arrival=flight_info.get("arrival", {}).get("scheduledTime"),
            actual_departure=flight_info.get("departure", {}).get("actualTime") or "Scheduled only",
            actual_arrival=flight_info.get("arrival", {}).get("actualTime") or "Scheduled only",
            terminal_departure=flight_info.get("departure", {}).get("terminal") or "Not assigned yet",
            terminal_arrival=flight_info.get("arrival", {}).get("terminal") or "Not assigned yet",
            gate_departure=flight_info.get("departure", {}).get("gate") or "Not assigned yet",
            gate_arrival=flight_info.get("arrival", {}).get("gate") or "Not assigned yet",
        )
        return flight
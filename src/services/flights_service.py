import os
from datetime import datetime
from typing import Union, List

from dotenv import load_dotenv

from config.databse import flights_collection
from src.models.flights_model import (
    FlightsListSearchRequest,
    FlightsListSearchResponse,
    FlightInfoResponse,
    FlightInfoRequest,
)
from amadeus import Client, ResponseError

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
            response = self.amadeus.schedule.flights.get(
                carrierCode=flight_info_request.airline,
                flightNumber=flight_info_request.flight_number,
                scheduledDepartureDate=flight_info_request.departure_date,
            )
            flight_data = response.data
        except ResponseError as error:
            print("Error in the Amadeus API request:", error)
            return []
        flight_info = flight_data[0]

        flight = FlightInfoResponse(
            flight_number=str(flight_info["flightDesignator"]["flightNumber"]),
            airline=str(flight_info["flightDesignator"]["carrierCode"]),
            status="Scheduled",
            departure_airport=str(flight_info["flightPoints"][0]["iataCode"]),
            arrival_airport=str(flight_info["flightPoints"][-1]["iataCode"]),
            scheduled_departure=str(flight_info["flightPoints"][0].get("departure", {}).get("timings", [{}])[0].get("value", "Unknown")),
            scheduled_arrival=str(flight_info["flightPoints"][-1].get("arrival", {}).get("timings", [{}])[0].get("value", "Unknown")),
            departure_time=str(flight_info["flightPoints"][0].get("departure", {}).get("timings", [{}])[0].get("value", "Unknown")),
            arrival_time=str(flight_info["flightPoints"][-1].get("arrival", {}).get("timings", [{}])[0].get("value", "Unknown")),
            duration=str(flight_info.get("segments", [{}])[0].get("scheduledSegmentDuration") or flight_info.get("legs", [{}])[0].get("scheduledLegDuration") or "Unknown"),
            actual_departure = "Scheduled only",
            actual_arrival = "Scheduled only",
            terminal_departure= "Not assigned yet",
            terminal_arrival= "Not assigned yet",
            gate_departure= "Not assigned yet",
            gate_arrival= "Not assigned yet",
        )
        return flight
    # Save flight search list in the databse
    async def save_flights_list(self,search_query:str, flights: List[dict], user_id: str=None):
        document = {
            "user_id": user_id,
            "query": search_query,
            "flights": [f.dict() for f in flights],
            "searched_at": datetime.now(),
        }
        result = flights_collection.insert_one(document)
        return str(result.inserted_id)
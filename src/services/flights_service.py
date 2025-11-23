import os
import uuid

from datetime import datetime
from typing import Union, List

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import Depends

from config.databse import flights_collection, users_collection
from src.models import BookFlightResponse, Itinerary

from src.models.flights_model import (
    FlightsListSearchRequest,
    FlightsListSearchResponse,
    FlightInfoResponse,
    FlightInfoRequest, Price, Flight, DeleteFlightResponse,
)
from amadeus import Client, ResponseError

from src.services.user_service import get_current_user
# from src.services import get_current_user
from src.utils import flights_parser
from src.utils.flights_parser import FlightQueryParser

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
            "includedAirlineCodes" : flight_request.airline,
        })
        params = {
            "originLocationCode": flight_request.departure_airport,
            "destinationLocationCode": flight_request.arrival_airport,
            "departureDate": str(flight_request.departure_date),
            "adults": flight_request.adults,
            "children": flight_request.children,
            "infants": flight_request.infants,
            "travelClass": flight_request.cabin_class,
            "currencyCode": flight_request.currency,
            "max": 5

        }
        # include only if the user has specified their prefered airline
        if flight_request.airline:
            params["includedAirlineCodes"] = flight_request.airline

        try:
            response = self.amadeus.shopping.flight_offers_search.get(**params)
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
    async def save_flights_list(self,search_query:str, flights: List[dict], user_id: str):
        document = {
            "user_id": get_current_user(user_id).id,
            "query": search_query,
            "flights": [f.dict() for f in flights],
            "searched_at": datetime.now(),
        }
        result = flights_collection.insert_one(document)
        return str(result.inserted_id)

    # Book a flight based on a user's query
    async def book_flight(self, search_query:str, user_email: str):
        # make sure that the user exists
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise ValueError("User not found")

        # search for flights using the function search flight lists
        flights_list = await self.search_flights_list(search_query)
        # handle the case where no flights were found in the flights list with the user's preferences
        if not flights_list:
            return BookFlightResponse(
                booking_id = str(uuid.uuid4()),
                booking_status = "Failed",
                itineraries=[],
                price=Price(total="0", currency="CAD", grand_total= "0.0")
            )
        # check the query, if the user has specified a flight number
        flight_info = self.parser.parse_query_flight_info(search_query)
        selected_flight = None
        if flight_info.flight_number:
            # loop through the list and find the flight with the specific number
            for flight in flights_list:
                if flight_info.flight_number == flight.flight_number:
                    selected_flight = flight
                    break
        # if no flight has been selected, select the first one in the list
        if not selected_flight:
            selected_flight = flights_list[0]

        print("This is the selected flight", selected_flight)
        # Book the flight, i.e add the flight to the flights colletion in the database
        booking_id = str(uuid.uuid4())
        booking_doc = {
            "_id": booking_id,
            "flight": selected_flight.flight_number,
            "departure_airport": selected_flight.departure_airport,
            "arrival_airport": selected_flight.arrival_airport,
            "departure_time": selected_flight.departure_time,
            "arrival_time": selected_flight.arrival_time,
            "booking_status": "Confirmed",
            "carrier_code": selected_flight.airline,
            "duration": selected_flight.duration,
            "price": {
                "total": selected_flight.price,
                "currency": "CAD",
                "grand_total": selected_flight.price,
        },
            "booked_at": datetime.now(),
        }
        # Insert the booking document into the flights collection
        flights_collection.insert_one(booking_doc)
        print("Flight booked successfully with booking ID:", booking_id)
        # Insert the flight booking into the user's booked flights list
        users_collection.update_one({
            "email": user_email,
        }, {
            "$push": { "booked_flights": booking_doc}},
        )
        # Prepare the response
        flight = Flight(
            flight_number=selected_flight.flight_number,
            departure_airport=selected_flight.departure_airport,
            arrival_airport=selected_flight.arrival_airport,
            departure_time=selected_flight.departure_time,
            arrival_time=selected_flight.arrival_time,
            duration=selected_flight.duration,
            carrier_code=selected_flight.airline,
        )
        itinerary = Itinerary(segments=[flight])
        price = Price(
            total=selected_flight.price,
            currency="CAD",
            grand_total=selected_flight.price,
        )
        booking_response = BookFlightResponse(
            booking_id=booking_id,
            booking_status="Confirmed",
            itineraries=[itinerary],
            price=price,
        )
        return booking_response

    # Delete a booked flight
    async def cancel_flight(self, query:str, user_email:str) -> DeleteFlightResponse:
        # Find the booking in the database
        booking_id = self.parser.parse_query_booking_id(query)
        if not booking_id:
            return DeleteFlightResponse(
                booking_id="",
                booking_status="Not Found",
                refund_amount="None",
            )
        # Delete the booking
        db_query = {"_id": booking_id}
        booking = flights_collection.find_one(db_query)
        # Make sure that the booking belongs to the user
        if booking["user_email"] != user_email:
            raise ValueError("You are not authorized to cancel this booking")
        flights_collection.update_one(
            {"_id": booking_id},
            {"$set": {"booking_status": "Cancelled"}}
        )
        # Also remove the booking from the user's booked flights list
        result = users_collection.update_one({
            "email": user_email,
            "booked_flights._id": booking_id,
        }, {
            "$set": {"booked_flights.$.booking_status": "Cancelled"}
        },
        )

        print("Matched:", result.matched_count, "Modified:", result.modified_count)
        print(users_collection.find_one({"email": user_email})["booked_flights"])

        # Prepare the response
        refund_price = Price(
            total=booking["price"]["total"],
            currency=booking["price"]["currency"],
            grand_total=booking["price"]["grand_total"],
        )
        return DeleteFlightResponse(
            booking_id=booking_id,
            booking_status="Cancelled",
            refund_amount=refund_price,
        )
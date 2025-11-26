import httpx
from fastapi import HTTPException, Query

from src.utils.http_helpers import request_with_retry
from src.utils.vacation_extractor import hybrid_extract

URL = "http://3.143.233.26:8000/api/v1"
async def get_recommendations( query: str = Query(..., description="Describe what kind of destination you want"),
    limit: int = Query(5, ge=1, le=20),
    user_id: str = Query(None, description="Optional user ID for personalized results")
):
    try:
        async with httpx.AsyncClient() as client:
            params = {"query": query, "limit": limit}
            if user_id:
                params["user_id"] = user_id

            response = await client.get(f"{URL}/destinations/recommendation", params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to get destination recommendations")

        data = response.json()
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def plan_vacation_service(user_raw_input: str, user_email: str, user_token: str):
    # Step 1 — Extract structured trip info
    trip = hybrid_extract(user_raw_input, schema_name="trip")
    print("Trip query:", trip)

    # Step 2 — Extract structured flight info
    flight = hybrid_extract(user_raw_input, schema_name="flight")
    print("Flight query:", flight)

    # Step 3 — Extract structured hotel info
    hotel_query = hybrid_extract(user_raw_input, schema_name="hotel")
    print("Hotel query:", hotel_query)

    payload_trip = {
        "destination": trip["trip"]["destination"],
        "budget": trip["trip"]["budget"],
        "duration": trip["trip"]["duration"],
        "number_of_travelers": trip["trip"]["number_of_travelers"],
        "date": trip["trip"]["date"]
    }

    payload_flight = {
        "departure_airport": flight["flight"]["departure_airport"],
        "arrival_airport": flight["flight"]["arrival_airport"],
        "departure_date": flight["flight"]["departure_date"],
        "cabin_class": flight["flight"]["cabin_class"],
        "adults": flight["flight"]["adults"],
        "children": flight["flight"].get("children", 0),
        "infants": flight["flight"].get("infants", 0)
    }

    hotel_dict = hotel_query["hotel"]
    user_input = f"Find hotels in {hotel_dict['destination']} from {hotel_dict['check_in']} to {hotel_dict['check_out']} for {hotel_dict['guests']} guests"

    payload_hotel = {
        "user_input": user_input
    }
    print("Hotel query:", payload_hotel)

    headers = {"Authorization": f"Bearer {user_token}"}

    async with httpx.AsyncClient() as client:

        # Trip create
        response_trip = await request_with_retry("post", f"{URL}/trips/", json=payload_trip, headers=headers)
        if response_trip.status_code != 200:
            raise Exception(f"Trips service returned {response_trip.status_code}: {response_trip.text}")

        # Hotel NLP Search
        response_hotels = await request_with_retry("post", f"{URL}/hotels", json=payload_hotel, headers=headers)
        if response_hotels.status_code != 200:
            raise Exception(f"Hotels service returned {response_hotels.status_code}: {response_hotels.text}")

        # Flights
        response_flights = await request_with_retry("post", f"{URL}/flights/", json=payload_flight, headers=headers)
        if response_flights.status_code != 200:
            raise Exception(f"Flights service returned {response_flights.status_code}: {response_flights.text}")

    return {
        "trip": response_trip.json(),
        "hotels": response_hotels.json(),
        "flights": response_flights.json()
    }

import httpx
from fastapi import HTTPException, Query

URL = "http://127.0.0.1:8000/api/v1"
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
#
# async def plan_trip(destination, email_address):
#     try:
#         async with httpx.AsyncClient() as client:
#             params = {"destination": destination, "email_address": email_address}
#             response = await client.get(f"{URL}/trips/create_trip", params=params)



async def plan_trip(trip, user_email: str, user_token: str):
    payload = {
        "destination": trip.destination,
        "budget": trip.budget,
        "duration": trip.duration,
        "number_of_travelers": trip.number_of_travelers,
        "date": trip.date.isoformat()  # convert datetime to string
    }

    headers = {"Authorization": f"Bearer {user_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{URL}/trips/",
            json=payload,
            headers=headers
        )

    if response.status_code != 200:
        raise Exception(f"Trips service returned {response.status_code}: {response.text}")

    return response.json()



#
# def search_flights_service():
#     print("hello")
#
# def search_hotels_service():
#     print("hello")
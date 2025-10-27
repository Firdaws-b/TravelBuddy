# TODO: Implement Trip service
import os
from urllib import request
from bson import ObjectId
from config.databse import trips_collection, client
from src.models.trip_model import PlannedTripModel,PlanATrip
from src.services.ai_service import generate_itinerary

async def plan_trip_service(destination, budget, duration,number_of_travelers, user_id):
    if trips_collection.find_one("destination", destination) and trips_collection.find_one("user_id", user_id):
        return {f"User has already a planned trip for the following destination {destination}"}

    # else call the hugging face model to plan a trip given the required trip info
    itinerary = await generate_itinerary(destination, duration,number_of_travelers,budget)









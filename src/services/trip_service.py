from datetime import datetime

from fastapi import HTTPException
from config.databse import trips_collection, client, users_collection
from src.models.trip_model import PlannedTripModel, PlanATrip, ItineraryDayModel
from src.services.ai_service import generate_itinerary, regenerate_itinerary

# Plan a trip
async def plan_trip_service(destination, budget, duration,number_of_travelers, user_email_address, date):
    # Check if the user already has a trip for this destination
    if trips_collection.find_one({"destination": destination, "user_email_address": user_email_address}):
        raise HTTPException(
            status_code=400,
            detail=f"User already has a planned trip for the destination: {destination}"
        )

    # Generate itinerary
    itinerary = await generate_itinerary(destination, duration,number_of_travelers,budget)
    # Add the trip along its generated itinerary to the database.
    # generated_itinerary = [day.model_dump() for day in itinerary]

    trip = PlannedTripModel(
        user_email_address= user_email_address,
        destination=destination,
        duration=duration,
        number_of_travelers=number_of_travelers,
        generated_itinerary=  itinerary,
        overall_cost=budget,
        cost_per_traveler=budget/number_of_travelers,
        planned_date_time=date
    )
    trip.generate_trip_id()
    trips_collection.insert_one(trip.model_dump())

    trip_dict = trip.dict()
    # remove the email_address to add the generated planned trip to the list of planned trips
    filtered_trip = {k: v for k, v in trip_dict.items() if k != "user_email_address"}
    # add the required trip to the list of trips under a user
    users_collection.update_one(
        {"email": user_email_address},
        {"$push":{"planned_trips": filtered_trip}}  )

    return trip

# return a summary of planned trips
def get_trips_service(user_email_address):
    # get all trips in the trips collection
    trips = trips_collection.find({"user_email_address":user_email_address}, {"_id":0, "trip_id":1, "destination":1, "duration":1, "overall_cost":1})
    return trips

# return all details of a planned trip
def get_planned_trip_service(trip_id, current_user_email_address):
    trip = trips_collection.find_one({"trip_id": trip_id, "user_email_address": current_user_email_address})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

async def update_trip_service(
    trip_id,
    duration,
    budget,
    number_of_travelers,
    planned_date_time,
    user_email_address
):
    trip = trips_collection.find_one({"trip_id": trip_id, "user_email_address": user_email_address})
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip with ID {trip_id} not found")

    # Keep old values if new ones not provided
    updated_duration = duration if duration is not None else trip["duration"]
    updated_budget = budget if budget is not None else trip["overall_cost"]
    updated_num_travelers = number_of_travelers if number_of_travelers is not None else trip["number_of_travelers"]
    updated_date = planned_date_time if planned_date_time is not None else trip["planned_date_time"]

    # Update DB
    trips_collection.update_one(
        {"trip_id": trip_id},
        {"$set": {
            "duration": updated_duration,
            "budget": updated_budget,
            "number_of_travelers": updated_num_travelers,
            "planned_date_time": updated_date
        }}
    )

    # Re-generate itinerary (only based on updated fields)
    itinerary = await generate_itinerary(
        trip["destination"],
        updated_duration,
        updated_num_travelers,
        updated_budget
    )

    trips_collection.update_one(
        {"trip_id": trip_id},
        {"$set": {"generated_itinerary": [day.model_dump() for day in itinerary]}}
    )

    # Update user’s planned trips list
    users_collection.update_one(
        {"email": trip["user_email_address"], "planned_trips.trip_id": trip_id},
        {"$set": {
            "planned_trips.$.duration": updated_duration,
            "planned_trips.$.number_of_travelers": updated_num_travelers,
            "planned_trips.$.overall_cost": updated_budget,
            "planned_trips.$.cost_per_traveler": updated_budget / updated_num_travelers,
            "planned_trips.$.planned_date_time": updated_date,
            "planned_trips.$.generated_itinerary": [day.model_dump() for day in itinerary]
        }}
    )

    return PlannedTripModel(
        user_email_address=trip["user_email_address"],
        destination=trip["destination"],
        duration=updated_duration,
        number_of_travelers=updated_num_travelers,
        generated_itinerary=itinerary,
        overall_cost=updated_budget,
        cost_per_traveler=updated_budget / updated_num_travelers,
        planned_date_time=updated_date
    )



def cancel_trip_service(trip_id, current_user_email_address):
    trip = trips_collection.find_one({"trip_id": trip_id, "user_email_address": current_user_email_address})
    if not trip:
        # Trip not found: raise 404 exception
        raise HTTPException(status_code=404, detail=f"Trip with ID: {trip_id} was not found")

    # remove from trip collection
    trips_collection.delete_one({"trip_id": trip_id})
    # remove from list of trips in of the user
    users_collection.update_one(
            {"email": trip["user_email_address"]},
            {"$pull": {"planned_trips": {"trip_id": trip_id}}}
        )
    return trip



async def regenerate_itinerary_service(trip_id, user_feedback, current_user_email_address):
    trip = trips_collection.find_one({"trip_id": trip_id, "user_email_address": current_user_email_address})
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip with ID: {trip_id} does not exist")

    users_collection.find_one()
    new_generated_itinerary = await regenerate_itinerary(trip, user_feedback)
    trips_collection.update_one(
            {"trip_id": trip_id, "user_email_address": current_user_email_address},
            {"$set": {"generated_itinerary": [day.model_dump() for day in new_generated_itinerary]}}
        )
    users_collection.update_one(
            {"email": trip["user_email_address"], "planned_trips.trip_id": trip_id},
            {"$set": {"planned_trips.$.generated_itinerary": [day.model_dump() for day in new_generated_itinerary],
                      }})

    return new_generated_itinerary



def get_itinerary_service(trip_id: str, user_email_address: str):
    trip = trips_collection.find_one(
        {"trip_id": trip_id, "user_email_address": user_email_address},
        {"_id": 0, "generated_itinerary": 1}
    )

    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip with ID {trip_id} not found")

    return trip["generated_itinerary"]










from datetime import datetime

from fastapi import HTTPException
from config.databse import trips_collection, client, users_collection
from src.models.trip_model import PlannedTripModel, PlanATrip, ItineraryDayModel
from src.services.ai_service import generate_itinerary

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
        cost_per_traveler=budget/duration,
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
def get_trips_service():
    # get all trips in the trips collection
    trips = trips_collection.find({}, {"_id":0, "trip_id":1, "destination":1, "duration":1, "overall_cost":1})
    return trips

# return all details of a planned trip
def get_planned_trip_service(trip_id):
    trip = trips_collection.find_one({"trip_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

# update a planned trip
async def update_trip_service(trip_id, duration, budget, number_of_travelers, planned_date_time):
    trip = trips_collection.find_one({"trip_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip with ID: {trip_id} does not exist")
    trips_collection.update_one(
            {"trip_id": trip_id},
            {"$set":{"duration": duration,"budget": budget,
                     "number_of_travelers": number_of_travelers,
                     "planned_date_time": planned_date_time,
                    }}
        )
    # generate a new itinerary with the new
    # updated fields: duration, budget, planned_date_time,
    #                 and number of travelers
    itinerary = await generate_itinerary(trip["destination"], duration, number_of_travelers, budget)
    trips_collection.update_one(
            {"trip_id": trip_id},
            {"$set": {"generated_itinerary": [day.model_dump() for day in itinerary]}}
        )
    updated_trip = PlannedTripModel(
            user_email_address=trip["user_email_address"],
            destination=trip["destination"],
            duration=duration,
            number_of_travelers=number_of_travelers,
            generated_itinerary=itinerary,
            overall_cost=budget,
            cost_per_traveler=budget / duration,
            planned_date_time=planned_date_time
        )

    # update user_planned trips
    users_collection.update_one(
            {"email": trip["user_email_address"], "planned_trips.trip_id": trip_id},
            {"$set": {"planned_trips.$.generated_itinerary": [day.model_dump() for day in itinerary],
                      "planned_trips.$.duration": duration,
                      "planned_trips.$.number_of_travelers": number_of_travelers,
                      "planned_trips.$.overall_cost": budget,
                      "planned_trips.$.cost_per_traveler": budget / duration,
                      "planned_trips.$.planned_date_time": planned_date_time
                      }}
    )
    return updated_trip


def cancel_trip_service(trip_id):
    trip = trips_collection.find_one({"trip_id": trip_id})
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



async def regenerate_itinerary_service(trip_id):
    trip = trips_collection.find_one({"trip_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip with ID: {trip_id} does not exist")

    users_collection.find_one()
    new_generated_itinerary = await generate_itinerary(trip["destination"], trip["duration"],trip["number_of_travelers"],2000)
    trips_collection.update_one(
            {"trip_id": trip_id},
            {"$set": {"generated_itinerary": [day.model_dump() for day in new_generated_itinerary]}}
        )
    users_collection.update_one(
            {"email": trip["user_email_address"], "planned_trips.trip_id": trip_id},
            {"$set": {"planned_trips.$.generated_itinerary": [day.model_dump() for day in new_generated_itinerary],
                      }})

    return new_generated_itinerary
        # Trip not found: raise HTTPException


def get_itinerary_service(trip_id: str):
    trip = trips_collection.find_one(
        {"trip_id": trip_id},
        {"_id": 0, "generated_itinerary": 1}
    )

    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip with ID {trip_id} not found")

    return trip["generated_itinerary"]










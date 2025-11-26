import requests
import uuid 

from pymongo import UpdateOne
from bson import ObjectId
from datetime import datetime, timezone
from config.settings import Settings
from config.databse import users_collection, hotels_collection, hotel_bookings_collection
from src.models.hotel_model import HotelModel

RAPIDAPI_HOST = Settings.RAPIDAPI_HOST
RAPIDAPI_KEY = Settings.RAPIDAPI_KEY


BASE_URL = f"https://{RAPIDAPI_HOST}/api/hotels/destination/search"


def search_hotels(q, check_in_date, check_out_date, adults, children, currency, gl, hl):
    headers = {
        "x-rapidapi-host": Settings.RAPIDAPI_HOST,
        "x-rapidapi-key": Settings.RAPIDAPI_KEY
    }

    params = {
        "q": q,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "adults": adults,
        "children": children,
        "currency": currency,
        "gl": gl,
        "hl": hl
    }

    params = {k: v for k, v in params.items() if v is not None}
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Error from RapidAPI: {response.status_code} - {response.text}")

    data = response.json()

    # Extract minimal hotel info to store/search
    hotels_summary = []
    for hotel in data.get("properties", []):
        hotels_summary.append({
            "hotel_id": hotel.get("place_id"), 
            "name": hotel.get("name"),
            "description": hotel.get("description"),
            "rating": hotel.get("overall_rating"),
            "reviews": hotel.get("reviews"),
            "price": hotel.get("rate_per_night", {}).get("extracted_lowest"),
            "currency": data.get("search_parameters", {}).get("currency"),
            "city": q
        })

    upsert_hotels(hotels_summary)
    hotels = []

    for hotel in hotels_summary:
        hotels.append(HotelModel(name=hotel["name"], description=hotel["description"], rating=hotel["rating"],
                                 price_per_night=hotel["price"], city=hotel["city"], currency=hotel["currency"]))
    return hotels
    # return hotels_summary



def create_booking_for_user(user: dict, booking_data: dict) -> dict:
    booking_doc = {
        "user_id": str(user["_id"]),
        "hotel_id": booking_data["hotel_id"],                                
        "check_in": booking_data["check_in"],
        "check_out": booking_data["check_out"],
        "adults": booking_data["adults"],
        "children": booking_data.get("children", 0),
        "status": "CONFIRMED",
        "confirmation_number": "HTL-" + str(uuid.uuid4())[:8],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    result = hotel_bookings_collection.insert_one(booking_doc)
    booking_doc["_id"] = str(result.inserted_id)
    return booking_doc

def get_bookings_by_user_id(user_id: str) -> list:
    """
    Retrieve all hotel bookings associated with a given user_id.
    """
    bookings = []
    cursor = hotel_bookings_collection.find({"user_id": user_id})
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["created_at"] = str(doc.get("created_at"))
        doc["updated_at"] = str(doc.get("updated_at"))
        bookings.append(doc)
    return bookings


def upsert_hotels(hotels: list):
    """Upsert each hotel by hotel_id into the hotels collection."""
    ops = []
    for h in hotels:
        if not h.get("hotel_id"):
            continue
        ops.append(
            UpdateOne(
                {"hotel_id": h["hotel_id"]},
                {
                    "$set": h,
                    "$setOnInsert": {
                        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                    },
                },
                upsert=True,
            )
        )
    if ops:
        hotels_collection.bulk_write(ops)

def update_booking_for_user(user_id: str, confirmation_number: str, update_data: dict):
    if not user_id or not confirmation_number:
        raise ValueError("User ID and confirmation number required")
    
    allowed_fields = {"check_in", "check_out", "adults", "children"}
    update_data = {k: v for k, v in update_data.items() if k in allowed_fields and v is not None}

    if not update_data:
        raise ValueError("No valid fields to update")
    
    update_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = hotel_bookings_collection.update_one(
        {"user_id": user_id, "confirmation_number": confirmation_number},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise ValueError("Booking not found with given confirmation number")
    
    updated_booking = hotel_bookings_collection.find_one(
        {"user_id": user_id, "confirmation_number": confirmation_number}
    )
    updated_booking["_id"] = str(updated_booking["_id"])
    return updated_booking


#############################################################
#
#                       DB OPERATIONS 
#
#############################################################

def list_bookings_by_user(user_id: str):
    bookings = []
    cursor = hotel_bookings_collection.find({"user_id": user_id})
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        bookings.append(doc)
    return bookings

def get_user_by_id(user_id: str) -> dict:
    """
    Load a user document by ObjectId string.
    Returns dict (without password) or None if not found.
    """
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user_id (not a valid ObjectId)")

    user = users_collection.find_one(
        {"_id": ObjectId(user_id)},
        {"password": 0}  # never return hashed passwords
    )
    return user
import requests
import uuid 

from bson import ObjectId
from datetime import datetime, timezone
from config.settings import Settings
from config.databse import users_collection, hotels_collection

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

    # remove None values
    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Error from RapidAPI: {response.status_code} - {response.text}")

    return response.json()


def create_booking_for_user(user: dict, booking_data: dict) -> dict:
    booking_doc = {
        "user_id": str(user["_id"]),
        "guest_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
        "email": user.get("email"),
        "phone": user.get("phone"),
        "hotel_name": booking_data.get("hotel_name"),
        "check_in": booking_data.get("check_in"),
        "check_out": booking_data.get("check_out"),
        "price": booking_data.get("price"),
        "currency": booking_data.get("currency"),
        "status": "CONFIRMED",
        "confirmation_number": "HTL-" + str(uuid.uuid4())[:8],
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }

    result = hotels_collection.insert_one(booking_doc)
    booking_doc["_id"] = str(result.inserted_id)
    return booking_doc

def get_bookings_by_user_id(user_id: str) -> list:
    """
    Retrieve all hotel bookings associated with a given user_id.
    """
    bookings = []
    cursor = hotels_collection.find({"user_id": user_id})
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["created_at"] = str(doc.get("created_at"))
        doc["updated_at"] = str(doc.get("updated_at"))
        bookings.append(doc)
    return bookings

#############################################################
#
#                       DB OPERATIONS 
#
#############################################################
def create_booking_record(booking_doc: dict):
    result = hotels_collection.insert_one(booking_doc)
    return str(result.inserted_id)

def list_bookings_by_user(user_id: str):
    bookings = []
    cursor = hotels_collection.find({"user_id": user_id})
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
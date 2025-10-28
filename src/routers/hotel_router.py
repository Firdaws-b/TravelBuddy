import logging

from bson import ObjectId
from fastapi import APIRouter, Query, HTTPException, Body, Path
from src.services.nlp_service import extract_hotel_search_params
from config.databse import hotel_bookings_collection
from src.models.hotel_model import BookingCreate
from src.services.hotel_service import (
    search_hotels, 
    create_booking_record, 
    get_user_by_id, 
    create_booking_for_user,
    get_bookings_by_user_id,
    upsert_hotels)


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/hotels", tags=["hotels"])
def hotel_search_with_nlp(
    user_input: str = Body(
        ...,
        embed=True,
        example="Find hotels in Montreal from November 15 to November 20 for 2 adults"
    )
):
    try:
        # 1. Extract data using NLP model
        extracted = extract_hotel_search_params(user_input)
        if not extracted.get("q"):
            raise HTTPException(status_code=400, detail="Destination not found in user input")

        # 2. Call hotel API with structured data
        response = search_hotels(**extracted)

        return {"query": extracted, "results": response}
        # return {"input": user_input, "result": extracted}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/hotels/{hotel_id}/bookings/{user_id}", tags=["hotels"])
def create_user_booking(
    hotel_id: str = Path(..., description="Hotel place_id / hotel_id"),
    user_id: str = Path(..., description="MongoDB ObjectId of the user"),
    booking_data: BookingCreate = Body(
        ...,
        example={
            "check_in": "2025-11-15",
            "check_out": "2025-11-20",
            "price": 300.00,
            "currency": "CAD"
        },
        description="Minimal booking details; hotel is provided in the path."
    )
):
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # (Optional) ensure hotel exists locally; you can add a quick lookup if you want
        new_booking = create_booking_for_user(user, hotel_id, booking_data.dict())

        return {
            "status": "success",
            "message": "Booking created successfully",
            "booking": new_booking
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hotels/bookings/{user_id}", tags=["hotels"])
def get_user_bookings(user_id: str = Path(..., description="MongoDB ObjectId of the user")):
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_bookings = get_bookings_by_user_id(user_id)
        if not user_bookings:
            return {
                "status": "success",
                "message": "No bookings found for this user",
                "bookings": []
            }

        return {
            "status": "success",
            "total": len(user_bookings),
            "bookings": user_bookings
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/hotels/{hotel_id}/bookings/{user_id}", tags=["hotels"])
def delete_booking(
    hotel_id: str = Path(..., description="Hotel ID (place_id)"),
    user_id: str = Path(..., description="MongoDB ObjectId of the user")
):
    """
    Delete all bookings by a user for a specific hotel_id.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id")

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = hotel_bookings_collection.delete_many({
        "hotel_id": hotel_id,
        "user_id": user_id
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No bookings found for this hotel and user")

    return {
        "status": "success",
        "message": f"Deleted {result.deleted_count} booking(s) for hotel {hotel_id} and user {user_id}"
    }
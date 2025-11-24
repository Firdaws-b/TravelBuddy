import logging

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Body, Path, Depends
from src.services.nlp_hotel_service import extract_hotel_search_params
from src.services.user_service import get_current_user
from config.databse import hotel_bookings_collection
from src.models.hotel_model import BookingCreate, BookingUpdate
from src.services.hotel_service import (
    search_hotels,  
    get_user_by_id, 
    create_booking_for_user,
    get_bookings_by_user_id,
    update_booking_for_user)


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/hotels", tags=["hotels"])
def hotel_search_with_nlp(
    user_input: str = Body(
        ...,
        embed=True,
        example="Find hotels in Montreal from November 15 to November 20 for 2 adults"
    ),
    current_user: dict = Depends(get_current_user)
):
    try:
        # 1. Extract data using NLP model
        extracted = extract_hotel_search_params(user_input)
        if not extracted.get("q"):
            raise HTTPException(status_code=400, detail="Destination not found in user input")

        # 2. Call hotel API with structured data
        # response = search_hotels(**extracted)

        # return {"query": extracted, "results": response}
        return {"input": user_input, "result": extracted}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/users/{user_id}/hotel-bookings", tags=["hotels"])
def create_user_booking(
    user_id: str = Path(..., description="MongoDB ObjectId of the user"),
    booking_data: BookingCreate = Body(
        ...,
        example={
            "hotel_id": "ChIJAfBnl0EayUwRqA8gLblTR_4",
            "check_in": "2025-11-15",
            "check_out": "2025-11-20",
            "adults": 2,
            "children": 0
        },
        description="Minimal booking details"
    ),
    current_user: dict = Depends(get_current_user)
):
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # (Optional) ensure hotel exists locally; you can add a quick lookup if you want
        new_booking = create_booking_for_user(user, booking_data.dict())

        return {
            "status": "success",
            "message": "Booking created successfully",
            "booking": new_booking
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/hotel-bookings", tags=["hotels"])
def get_user_bookings(user_id: str = Path(..., description="MongoDB ObjectId of the user"), current_user: dict = Depends(get_current_user)):
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


@router.put("/users/{user_id}/hotel-bookings/confirmation/{confirmation_number}", tags=["hotels"])
def update_booking(
    user_id :  str = Path(..., description="MongoDB ObjectId of the user"),
    confirmation_number: str = Path(..., description="Booking confirmation number"),
    booking_update: BookingUpdate = Body(..., description="Fields to update"),
    current_user: dict = Depends(get_current_user)
):
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        updated_booking = update_booking_for_user(user_id, confirmation_number, booking_update.dict())
        return {
            "status": "success",
            "message": "Booking updated successfully",
            "updated_booking": updated_booking
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/users/{user_id}/hotel-bookings/confirmation/{confirmation_number}", tags=["hotels"])
def delete_booking_by_confirmation(
    user_id: str = Path(..., description="MongoDB ObjectId of the user"),
    confirmation_number: str = Path(..., description="Booking confirmation number"),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Validate user
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Delete booking by confirmation number
        result = hotel_bookings_collection.delete_one({
            "user_id": user_id,
            "confirmation_number": confirmation_number
        })

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No booking found for confirmation number {confirmation_number}"
            )

        return {
            "status": "success",
            "message": f"Booking with confirmation number {confirmation_number} deleted successfully"
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator


DATE_FMT = "%Y-%m-%d"


class BookingCreate(BaseModel):
    hotel_id: str = Field(..., example="ChIJAfBnl0EayUwRqA8gLblTR_4")
    check_in: str = Field(..., example="2025-11-15")
    check_out: str = Field(..., example="2025-11-20")
    adults: int = Field(..., gt=0, example=2, description="Number of adults")
    children: int = Field(0, ge=0, example=1, description="Number of children")

    @model_validator(mode="after")
    def validate_dates(self):
        """
        Ensures check_out is after check_in.
        Runs after all fields are parsed (Pydantic v2 style).
        """
        try:
            ci = datetime.strptime(self.check_in, DATE_FMT)
            co = datetime.strptime(self.check_out, DATE_FMT)
        except ValueError:
            raise ValueError("Dates must follow YYYY-MM-DD format")

        if co <= ci:
            raise ValueError("check_out must be after check_in")
        return self

class HotelModel(BaseModel):
    name: str
    description: str
    rating: float
    price_per_night: float
    city: str
    currency: str

class BookingUpdate(BaseModel):
    check_in: Optional[str] = Field(None, example="2025-11-18")
    check_out: Optional[str] = Field(None, example="2025-11-22")
    adults: Optional[int] = Field(None, gt=0, example=2)
    children: Optional[int] = Field(None, ge=0, example=1)

    @model_validator(mode="after")
    def validate_dates(self):
        """
        Only checks date order if both check_in and check_out are provided.
        """
        if not self.check_in or not self.check_out:
            return self  # Nothing to validate if one is missing

        try:
            ci = datetime.strptime(self.check_in, DATE_FMT)
            co = datetime.strptime(self.check_out, DATE_FMT)
        except ValueError:
            raise ValueError("Dates must follow YYYY-MM-DD format")

        if co <= ci:
            raise ValueError("check_out must be after check_in")
        return self



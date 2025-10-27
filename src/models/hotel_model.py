from datetime import datetime
from pydantic import BaseModel, Field, validator

class HotelSearchInput(BaseModel):
    user_input: str = Field(
        ...,
        example="Find hotels in Montreal from November 15 to November 20 for 2 adults",
        description="A natural language query to search hotels."
    )

class HotelBookingInput(BaseModel):
    hotel_name: str = Field(..., example="Hilton Downtown")
    city: str = Field(..., example="Montréal")
    address: str = Field(..., example="123 Rue Sainte-Catherine O, Montréal, QC H3B 1A7")
    check_in: str = Field(..., example="2025-11-15")
    check_out: str = Field(..., example="2025-11-20")
    price: float = Field(..., gt=0, example=500.00)
    currency: str = Field(..., min_length=3, max_length=3, example="CAD")

    @validator("check_out")
    def check_dates(cls, v, values):
        check_in = datetime.strptime(values["check_in"], "%Y-%m-%d")
        check_out = datetime.strptime(v, "%Y-%m-%d")
        if check_out <= check_in:
            raise ValueError("check_out must be after check_in")
        return v

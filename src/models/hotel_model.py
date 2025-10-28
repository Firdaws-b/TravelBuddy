from datetime import datetime
from pydantic import BaseModel, Field, validator

class BookingCreate(BaseModel):
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

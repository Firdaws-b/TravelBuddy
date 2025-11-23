from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

from src.models.trip_model import PlannedTripModel


class CreateUser(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str


class UserProfile(BaseModel):
    email: str
    first_name: str
    last_name: str
    budget_range: Optional[dict] = None
    planned_trips: Optional[List[PlannedTripModel]] = None
    activity_preferences: List[dict] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    password_hash: str
    role: str = "user"


class UserLogin(BaseModel):
    email: str
    password: str

class UpdateUser(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    budget_range: Optional[dict] = None
    activity_preferences: Optional[dict] = None


class UserFeedback(BaseModel):
    user_feedback: str

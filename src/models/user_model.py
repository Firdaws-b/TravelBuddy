from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
class CreateUser(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime
    password_hash: str


class UserProfile(BaseModel):
    email: str
    first_name: str
    last_name: str
    budget_range: Optional[dict] = None
    planned_trips: Optional[dict] = None
    activity_preferences: List[dict] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    password_hash: str

class UserLogin(BaseModel):
    email: str
    password: str



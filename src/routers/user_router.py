# Manages user resources (signup, profile, updates
# reserved for CRUD operations (Create, Read, Update, Delete)

from fastapi import APIRouter, Depends
from src.models.user_model import UserLogin, CreateUser, UpdateUser
from src.services.user_service import create_user, login_user, get_current_user, update_user_function

router = APIRouter(prefix="/users", tags=["users"])
@router.post("")
def sign_up(user:CreateUser):
    return create_user(user.email, user.password,user.first_name, user.last_name)

# Return the current authenticated user
@router.get("/user")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {"Welcome ": current_user["first_name"] + " " + current_user["last_name"]}

# update user info
@router.put("/{user_id}")
async def update_user(user_id,user_new_data: UpdateUser):
    updated_user = update_user_function(user_id, user_new_data)
    return updated_user


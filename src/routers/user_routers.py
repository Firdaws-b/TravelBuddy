from fastapi import APIRouter, Depends
from src.models.user_model import UserLogin, CreateUser
from src.services.user_service import create_user, login_user, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/login")
def login(user:UserLogin):
    return login_user(user.email, user.password)

@router.post("/signup")
def signup(user:CreateUser):
    return create_user(user.email, user.password,user.first_name, user.last_name)

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {"Welcome ": current_user["first_name"] + " " + current_user["last_name"]}

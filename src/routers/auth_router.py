# Manages authentication (login, logout)
from fastapi import APIRouter, Depends
from src.models.user_model import UserLogin, CreateUser
from src.services.user_service import create_user, login_user, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token")
def login(user:UserLogin):
    return login_user(user.email, user.password)
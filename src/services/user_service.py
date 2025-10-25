import os
from config.databse import users_collection, client
from src.core.security import hash_password, verify_password, create_token
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

JWT_SECRET = os.getenv('JWT_SECRET_KEY')
security = HTTPBearer() # to return the token from the header

def create_user(email, password, first_name, last_name):
    if users_collection.find_one({'email': email}):
        return {"error": "User already exists"}
    users_collection.insert_one({"email": email, "password": hash_password(password), "first_name": first_name, "last_name": last_name})
    return {"msg": "User created successfully"}

def get_user(email):
    return users_collection.find_one({'email': email})

def login_user(email, password):
    user = users_collection.find_one({'email': email})
    if not user or not verify_password(password, user['password']):
        return {"error": "Invalid credentials"}
    token = create_token({"email":email})
    return {"User logged in successfully, access_token": token}

# return the current user
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        email: str = payload['email']
        user = get_user(email)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        db = client["TravelBuddy"]
        user_collection = db["Users"]
        print("user collection is ********: ", user_collection)
        user = user_collection.find_one({"email": email})
        print("email is ", email)
        print("user: ", user)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user['_id'] = str(user['_id'])
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")


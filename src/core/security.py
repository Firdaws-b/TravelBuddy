from passlib.context import CryptContext
import jwt, os
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

def hash_password(password):
    return pwd_context.hash(password)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password):
    return pwd_context.hash(password)
def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")






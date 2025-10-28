import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
load_dotenv()

class Settings:
    MONGO_URI = os.getenv("MONGO_URI")
    BASE_ROUTE: str = "/api/v1"
    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

settings = Settings()

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
load_dotenv()

class Settings:
    MONGO_URI = os.getenv("MONGO_URI")
    BASE_ROUTE: str = "/api/v1"
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

settings = Settings()

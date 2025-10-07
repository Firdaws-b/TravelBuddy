from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_ROUTE: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
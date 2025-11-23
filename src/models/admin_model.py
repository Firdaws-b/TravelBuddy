from openai import BaseModel
# import secrets
# api_key = secrets.token_urlsafe(32)


class AdminModel(BaseModel):
    name: str
    api_key: str
    role: str = "admin"

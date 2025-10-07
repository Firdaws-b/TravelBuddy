import warnings
from fastapi.testclient import TestClient
from main import app

warnings.filterwarnings("ignore", category=DeprecationWarning)

client = TestClient(app)

def test_hotel_routes():
    response = client.get("/api/v1/hotels")
    assert response.status_code == 200 
    assert "message" in response.json()


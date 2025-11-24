import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.main import app
from config.databse import recommendations_collection, users_collection

client = TestClient(app)

# ----------------------
# Helpers
# ----------------------

def setup_test_user():
    #users_collection.delete_many({})
    user = {
        "email": "test@example.com",
        "password": "hashed",
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
        "preferences": {
            "interests": ["beach", "nightlife"],
            "budget": 1500
        }
    }
    inserted = users_collection.insert_one(user)
    return str(inserted.inserted_id)

def clear_recommendations():
    recommendations_collection.delete_many({})

# ----------------------
# Mock embedding vector
# ----------------------
def mock_embed_vector(*args, **kwargs):
    """Return a fixed-size embedding vector to avoid calling OpenAI."""
    return [0.1] * 1536  # text-embedding-3-small returns 1536 dims


# ----------------------
# Tests
# ----------------------
@pytest.fixture
def test_user_id():
    return setup_test_user()


@pytest.fixture(autouse=True)
def clean_recommendations():
    recommendations_collection.delete_many({})


@patch("src.services.destination_service._embed_text", return_value=mock_embed_vector())
def test_recommend_endpoint(mock_embed, test_user_id):
    response = client.get(
        "/destinations/recommendation",
        params={"query": "warm beach", "limit": 3, "user_id": test_user_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)


@patch("src.services.destination_service._embed_text", return_value=mock_embed_vector())
def test_create_recommendation(mock_embed, test_user_id):
    response = client.post(
        "/destinations/recommendations",
        params={"user_id": test_user_id, "query": "cheap tropical", "limit": 3}
    )
    assert response.status_code == 200
    res = response.json()
    assert "_id" in res
    assert res["user_id"] == test_user_id


@patch("src.services.destination_service._embed_text", return_value=mock_embed_vector())
def test_get_past_recommendations(mock_embed, test_user_id):
    # Create recommendation first
    client.post(
        "/destinations/recommendations",
        params={"user_id": test_user_id, "query": "beach place", "limit": 3}
    )

    # Retrieve past recommendations
    response = client.get(f"/destinations/recommendations/{test_user_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@patch("src.services.destination_service._embed_text", return_value=mock_embed_vector())
def test_regenerate_recommendation(mock_embed, test_user_id):

    # Create recommendation
    res = client.post(
        "/destinations/recommendations",
        params={"user_id": test_user_id, "query": "old prompt", "limit": 3}
    ).json()

    rec_id = res["_id"]

    # Regenerate
    response = client.put(
        f"/destinations/recommendations/{rec_id}/regenerate",
        params={"new_query": "new prompt", "limit": 3}
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["_id"] == rec_id
    assert updated["original_query"] == "new prompt"


@patch("src.services.destination_service._embed_text", return_value=mock_embed_vector())
def test_delete_recommendation(mock_embed, test_user_id):

    # Create first
    res = client.post(
        "/destinations/recommendations",
        params={"user_id": test_user_id, "query": "delete this", "limit": 3}
    ).json()

    rec_id = res["_id"]

    # Delete
    response = client.delete(f"/destinations/recommendations/{rec_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Recommendation deleted"

    # Should not exist anymore
    history = client.get(f"/destinations/recommendations/{test_user_id}").json()
    assert rec_id not in [r["_id"] for r in history]

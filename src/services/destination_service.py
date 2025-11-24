import numpy as np
from bson import ObjectId
from datetime import datetime, timezone
from huggingface_hub import InferenceClient
from config.databse import db, users_collection, destinations_collection
from config.settings import settings


#############################################################
#
#                       AI MODEL SETUP
#
#############################################################
client = InferenceClient(
    model="sentence-transformers/all-mpnet-base-v2",
    token=settings.HF_TOKEN
)


#############################################################
#
#                       CORE FUNCTIONS
#
#############################################################
def get_all_destinations(limit: int = 100) -> list:
    """
    Retrieve all destinations from the database.
    Converts ObjectIds to strings for JSON serialization.
    """
    cursor = destinations_collection.find().limit(limit)
    data = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        data.append(doc)
    return data


def _embed_text(text: str):
    """
    Convert text to vector embeddings using Hugging Face.
    """
    arr = client.feature_extraction(text)
    return np.mean(np.array(arr), axis=0)


def _cosine(a, b):
    """
    Compute cosine similarity between two embedding vectors.
    """
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def recommend_destinations(query: str, limit: int = 5, user_prefs: dict = None):
    """
    Recommend destinations based on a text query and optional user preferences.
    Uses semantic similarity (embedding vectors) for ranking.
    """
    # Merge user preferences into the query for personalization
    if user_prefs:
        prefs_text = ""
        if "interests" in user_prefs:
            prefs_text += " " + " ".join(user_prefs["interests"])
        if "budget" in user_prefs:
            prefs_text += f" budget {user_prefs['budget']}"
        query = query + prefs_text

    query_vec = _embed_text(query)
    destinations = get_all_destinations(limit=100)
    scored = []

    for dest in destinations:
        text = f"{dest.get('name', '')} {dest.get('description', '')} {' '.join(dest.get('tags', []))}"
        dest_vec = _embed_text(text)
        score = _cosine(query_vec, dest_vec)

        # Budget-based adjustment (optional, light influence)
        avg_cost = dest.get("average_cost", 0)
        if user_prefs and "budget" in user_prefs and avg_cost:
            budget = float(user_prefs["budget"])
            cost_penalty = abs(avg_cost - budget) / budget
            score *= (1 - 0.3 * cost_penalty)

        scored.append((score, dest))

    scored.sort(key=lambda x: x[0], reverse=True)
    result = []
    for _, dest in scored[:limit]:
        dest["_id"] = str(dest["_id"])
        result.append(dest)

    return result


#############################################################
#
#                       DB OPERATIONS
#
#############################################################
def get_user_by_id(user_id: str) -> dict:
    """
    Load a user document by ObjectId string.
    Returns dict (without password) or None if not found.
    """
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user_id (not a valid ObjectId)")

    user = users_collection.find_one(
        {"_id": ObjectId(user_id)},
        {"password": 0}
    )
    return user


def upsert_destinations(destinations: list):
    """
    Upsert multiple destination documents into MongoDB.
    Similar to hotel upserts.
    """
    from pymongo import UpdateOne
    ops = []
    for d in destinations:
        if not d.get("name"):
            continue
        ops.append(
            UpdateOne(
                {"name": d["name"], "country": d.get("country")},
                {
                    "$set": d,
                    "$setOnInsert": {
                        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                    },
                },
                upsert=True,
            )
        )
    if ops:
        destinations_collection.bulk_write(ops)

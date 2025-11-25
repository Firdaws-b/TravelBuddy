import os
import numpy as np
from bson import ObjectId
from datetime import datetime, timezone
from openai import OpenAI

from config.databse import db, users_collection, destinations_collection, recommendations_collection
from config.settings import settings

# AI model setup (OpenAI embeddings)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY_OTHER"))
EMBED_MODEL = "text-embedding-3-small"


# Core functions
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


def _embed_text(text: str, is_query: bool = False) -> np.ndarray:
    """
    Convert text to vector embeddings using OpenAI.
    Prefix text slightly differently for queries vs destination docs.
    """
    if is_query:
        text = "user request: " + text
    else:
        text = "destination description: " + text

    response = openai_client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return np.array(response.data[0].embedding)


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

    query_vec = _embed_text(query, is_query=True)
    destinations = get_all_destinations(limit=100)
    scored = []

    for dest in destinations:
        text = f"{dest.get('name', '')} {dest.get('description', '')} {' '.join(dest.get('tags', []))}"
        dest_vec = _embed_text(text, is_query=False)
        score = _cosine(query_vec, dest_vec)

        # Budget-based adjustment (optional, light influence)
        avg_cost = dest.get("average_cost", 0)
        if user_prefs and "budget" in user_prefs and avg_cost:
            budget = float(user_prefs["budget"])
            if budget > 0:
                cost_penalty = abs(avg_cost - budget) / budget
                score *= (1 - 0.3 * cost_penalty)

        scored.append((score, dest))

    scored.sort(key=lambda x: x[0], reverse=True)
    result = []
    for _, dest in scored[:limit]:
        dest["_id"] = str(dest["_id"])
        result.append(dest)

    return result


# DB operations and recommendation history
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


def create_recommendation(user_id: str, query: str, limit: int = 5):
    user = get_user_by_id(user_id)
    user_prefs = user.get("preferences", {}) if user else {}

    results = recommend_destinations(query, limit, user_prefs)

    doc = {
        "user_id": user_id,
        "original_query": query,
        "results": results,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    inserted = recommendations_collection.insert_one(doc)
    doc["_id"] = str(inserted.inserted_id)
    return doc


def get_past_recommendations(user_id: str):
    cursor = recommendations_collection.find({"user_id": user_id}).sort("created_at", -1)
    recs = []
    for rec in cursor:
        rec["_id"] = str(rec["_id"])
        recs.append(rec)
    return recs


def regenerate_recommendation(rec_id: str, new_query: str, limit: int = 5):
    if not ObjectId.is_valid(rec_id):
        raise ValueError("Invalid recommendation ID")

    rec = recommendations_collection.find_one({"_id": ObjectId(rec_id)})
    if not rec:
        raise ValueError("Recommendation not found")

    user_id = rec["user_id"]
    user = get_user_by_id(user_id)
    user_prefs = user.get("preferences", {}) if user else {}

    # Generate new results based on edited query
    results = recommend_destinations(new_query, limit, user_prefs)

    recommendations_collection.update_one(
        {"_id": ObjectId(rec_id)},
        {
            "$set": {
                "original_query": new_query,
                "results": results,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        },
    )

    updated = recommendations_collection.find_one({"_id": ObjectId(rec_id)})
    updated["_id"] = str(updated["_id"])
    return updated


def delete_recommendation(rec_id: str):
    if not ObjectId.is_valid(rec_id):
        raise ValueError("Invalid recommendation ID")

    result = recommendations_collection.delete_one({"_id": ObjectId(rec_id)})
    return result.deleted_count == 1

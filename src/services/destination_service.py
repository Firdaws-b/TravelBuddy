import numpy as np
from huggingface_hub import InferenceClient
from config.databse import db
from config.settings import settings

# Hugging Face client
client = InferenceClient(
    model="sentence-transformers/all-mpnet-base-v2",
    token=settings.HF_TOKEN
)

# MongoDB collection
destinations_collection = db["Destinations"]

def get_all_destinations(limit: int = 100):
    cursor = destinations_collection.find().limit(limit)
    destinations = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])   
        destinations.append(doc)
    return destinations

def _embed_text(text: str):
    arr = client.feature_extraction(text)
    return np.mean(np.array(arr), axis=0)

def _cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def recommend_destinations(query: str, limit: int = 5):
    query_vec = _embed_text(query)
    destinations = get_all_destinations(limit=100)  # get all, rank manually
    scored = []

    for dest in destinations:
        text = f"{dest.get('name', '')} {dest.get('description', '')} {' '.join(dest.get('tags', []))}"
        dest_vec = _embed_text(text)
        score = _cosine(query_vec, dest_vec)
        scored.append((score, dest))

    scored.sort(key=lambda x: x[0], reverse=True)
    result = []
    for _, dest in scored[:limit]:
        dest["_id"] = str(dest["_id"])  
        result.append(dest)

    return result

from config.databse import db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def seed():
    # ---------- Seed Destinations ----------
    destinations = [
    {
        "name": "Bali",
        "country": "Indonesia",
        "description": "Tropical island known for beaches, temples, yoga retreats, and surfing.",
        "tags": ["beach", "tropical", "surfing", "nightlife", "wellness"],
        "best_time_to_visit": "April–October",
        "average_cost": 1200.0
    },
    {
        "name": "Kyoto",
        "country": "Japan",
        "description": "Cultural city with temples, cherry blossoms, and a calm atmosphere.",
        "tags": ["culture", "temples", "calm", "history", "food"],
        "best_time_to_visit": "March–May, October–November",
        "average_cost": 2000.0
    },
    {
        "name": "Cancún",
        "country": "Mexico",
        "description": "Beach destination with all-inclusive resorts, nightlife, and water sports.",
        "tags": ["beach", "resorts", "party", "nightlife", "water-sports"],
        "best_time_to_visit": "December–April",
        "average_cost": 1400.0
    },
    {
        "name": "Paris",
        "country": "France",
        "description": "Romantic city known for art, fashion, fine dining, and iconic landmarks.",
        "tags": ["romantic", "art", "fashion", "culture", "city-life"],
        "best_time_to_visit": "April–June, September–November",
        "average_cost": 2200.0
    },
    {
        "name": "Banff",
        "country": "Canada",
        "description": "Mountain town famous for hiking, skiing, and turquoise lakes in the Rockies.",
        "tags": ["mountains", "hiking", "nature", "skiing", "lakes"],
        "best_time_to_visit": "June–August, December–March",
        "average_cost": 1800.0
    },
    {
        "name": "Dubai",
        "country": "United Arab Emirates",
        "description": "Luxury destination with shopping malls, beaches, desert safaris, and nightlife.",
        "tags": ["luxury", "shopping", "desert", "nightlife", "modern"],
        "best_time_to_visit": "November–March",
        "average_cost": 2500.0
    },
    {
        "name": "Santorini",
        "country": "Greece",
        "description": "Picturesque island with whitewashed houses, blue domes, and sunsets over the Aegean.",
        "tags": ["romantic", "beach", "scenic", "island", "relaxation"],
        "best_time_to_visit": "April–October",
        "average_cost": 1700.0
    },
    {
        "name": "Reykjavik",
        "country": "Iceland",
        "description": "Gateway to glaciers, waterfalls, and the Northern Lights.",
        "tags": ["adventure", "nature", "northern-lights", "geysers", "cold"],
        "best_time_to_visit": "February–April, September–October",
        "average_cost": 2300.0
    },
    {
        "name": "Marrakesh",
        "country": "Morocco",
        "description": "Vibrant city with bustling souks, historic palaces, and desert excursions.",
        "tags": ["culture", "markets", "history", "desert", "exotic"],
        "best_time_to_visit": "March–May, September–November",
        "average_cost": 1500.0
    },
    {
        "name": "Cape Town",
        "country": "South Africa",
        "description": "Coastal city with Table Mountain views, beaches, vineyards, and wildlife safaris nearby.",
        "tags": ["beach", "mountains", "wine", "nature", "adventure"],
        "best_time_to_visit": "November–March",
        "average_cost": 1600.0
    }
    ]


    destinations_collection = db["Destinations"]
    destinations_collection.delete_many({})  # clear existing
    result_dest = destinations_collection.insert_many(destinations)
    print(f"Inserted {len(result_dest.inserted_ids)} destinations.")
    

#     # ---------- Seed Example Users ----------
#     users = [
#         {
#             "email": "beachlover@example.com",
#             "password": hash_password("password123"),
#             "first_name": "Maya",
#             "last_name": "Santos",
#             "role": "user",
#             "preferences": {
#                 "interests": ["beach", "nightlife", "tropical"],
#                 "budget": 1300
#             }
#         },
#         {
#             "email": "culturefan@example.com",
#             "password": hash_password("password123"),
#             "first_name": "Kenji",
#             "last_name": "Tanaka",
#             "role": "user",
#             "preferences": {
#                 "interests": ["culture", "temples", "calm"],
#                 "budget": 2200
#             }
#         },
#         {
#             "email": "partygoer@example.com",
#             "password": hash_password("password123"),
#             "first_name": "Alex",
#             "last_name": "Rivera",
#             "role": "user",
#             "preferences": {
#                 "interests": ["nightlife", "resorts", "party"],
#                 "budget": 1500
#             }
#         }
#     ]

#     users_collection = db["Users"]
#     users_collection.delete_many({})  # clear existing
#     result_users = users_collection.insert_many(users)
#     print(f"Inserted {len(result_users.inserted_ids)} users with preferences.")

#     print("\nUser IDs for testing personalization:")
#     for user, user_id in zip(users, result_users.inserted_ids):
#         print(f"- {user['email']}: {user_id}")
if __name__ == "__main__":
    seed()

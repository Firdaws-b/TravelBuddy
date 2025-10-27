from config.databse import db

def seed():
    destinations = [
        {
            "name": "Bali",
            "country": "Indonesia",
            "description": "Tropical island known for beaches, temples, and surfing.",
            "tags": ["beach", "tropical", "surfing", "nightlife", "wellness"],
            "best_time_to_visit": "April–October",
            "average_cost": 1200.0
        },
        {
            "name": "Kyoto",
            "country": "Japan",
            "description": "Cultural city with temples and calm atmosphere.",
            "tags": ["culture", "temples", "calm", "history"],
            "best_time_to_visit": "March–May, October–November",
            "average_cost": 2000.0
        },
        {
            "name": "Cancún",
            "country": "Mexico",
            "description": "Beach destination with resorts and nightlife.",
            "tags": ["beach", "resorts", "party", "nightlife"],
            "best_time_to_visit": "December–April",
            "average_cost": 1400.0
        }
    ]

    collection = db["Destinations"]

    # await collection.delete_many({})
    result = collection.insert_many(destinations)

    #print("Seed complete! Inserted sample destinations into MongoDB.")
    print(f"Inserted {len(result.inserted_ids)} destinations.")

if __name__ == "__main__":
    seed()


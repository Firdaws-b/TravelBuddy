from pymongo.mongo_client import MongoClient
import certifi
from config.settings import settings

client = MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())
db = client["TravelBuddy"]
users_collection = db["Users"]
trips_collection = db["Trips"]
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)




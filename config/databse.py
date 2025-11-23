from pymongo.mongo_client import MongoClient
import certifi
from config.settings import settings

client = MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())
db = client["TravelBuddy"]
users_collection = db["Users"]
destinations_collection = db["Destinations"]
trips_collection = db["Trips"]
hotels_collection = db["hotels"]
hotel_bookings_collection = db["hotel_bookings"]
admins_collection = db["Admins"]
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)




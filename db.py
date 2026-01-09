from pymongo import MongoClient
import os

# ✅ use the ENV VAR NAME, not the value
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI environment variable not set")

print("✅ Using MongoDB Atlas")

client = MongoClient(MONGO_URI)

db = client["knowledge-base"]
collection = db["data-for-ai"]

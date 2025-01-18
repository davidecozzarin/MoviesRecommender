from pymongo import MongoClient
import bcrypt
from datetime import datetime, timezone
import os

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("La variabile d'ambiente MONGO_URI non è definita.")

client = MongoClient(MONGO_URI)
db = client["FilmRecommender"]
users_collection = db["users"]

def register_user(username, password, profile_pic=None):
    # Controlla se l'utente esiste già
    if users_collection.find_one({"username": username}):
        return "Username already exists."
    
    # Hash della password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = {
        "username": username,
        "password_hash": hashed_password,
        "profile_pic": profile_pic,
        "preferences": [],
        "disliked": [],
        "created_at": datetime.now(timezone.utc)
    }
    users_collection.insert_one(user)
    return "User registered successfully."

def authenticate_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"]):
        return True, user
    return False, None

def get_user(username):
    return users_collection.find_one({"username": username})

def update_preferences(username, preferences):
    user = users_collection.find_one({"username": username})
    if not user:
        return "User not found."
    
    users_collection.update_one(
        {"username": username},
        {"$set": {"preferences": preferences}}
    )
    return "Preferences updated successfully."

def get_preferences(username):
    user = users_collection.find_one({"username": username})
    if user:
        return user["preferences"]
    return []

def update_disliked(username, disliked):
    user = users_collection.find_one({"username": username})
    if not user:
        return "User not found."
    
    users_collection.update_one(
        {"username": username},
        {"$set": {"disliked": disliked}}
    )
    return "Preferences updated successfully."

def get_disliked(username):
    user = users_collection.find_one({"username": username})
    if user:
        return user["disliked"]
    return []


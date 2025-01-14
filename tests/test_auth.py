import os
from pymongo import MongoClient
from src.auth import (
    register_user,
    authenticate_user,
    get_user,
    update_preferences,
    get_preferences,
    update_disliked,
    get_disliked,
)
from mongomock import MongoClient as MockMongoClient


# Usa un client mock durante i test
if os.getenv("TEST_ENV", "false").lower() == "true":
    client = MockMongoClient()
else:
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))

db = client["FilmRecommender"]

def setup_module(module):
    db["users"].delete_many({})

def teardown_module(module):
    db["users"].delete_many({})  

def test_register_user_existing():
    register_user("test_existing_user", "password123")
    result = register_user("test_existing_user", "password456")
    assert result == "Username already exists."

def test_authenticate_invalid_user():
    authenticated, user = authenticate_user("test_invalid_user", "invalid_pass")
    assert authenticated is False
    assert user is None

def test_get_user():
    register_user("test_user", "password123")
    user = get_user("test_user")
    assert user is not None
    assert user["username"] == "test_user"

def test_update_preferences():
    register_user("test_user", "password123")
    update_result = update_preferences("test_user", [1, 2, 3])
    assert update_result == "Preferences updated successfully."
    preferences = get_preferences("test_user")
    assert preferences == [1, 2, 3]

def test_get_preferences():
    register_user("test_user", "password123")
    update_preferences("test_user", [4, 5, 6])
    preferences = get_preferences("test_user")
    assert preferences == [4, 5, 6]

def test_update_disliked():
    register_user("test_user", "password123")
    update_result = update_disliked("test_user", [10, 11, 12])
    assert update_result == "Preferences updated successfully."
    disliked = get_disliked("test_user")
    assert disliked == [10, 11, 12]

def test_get_disliked():
    register_user("test_user", "password123")
    update_disliked("test_user", [20, 21, 22])
    disliked = get_disliked("test_user")
    assert disliked == [20, 21, 22]

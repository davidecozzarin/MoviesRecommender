import pytest
from src.auth import (
    register_user,
    authenticate_user,
    get_user,
    update_preferences,
    get_preferences,
    update_disliked,
    get_disliked,
)
from pymongo import MongoClient
import os

# Configurazione del client MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["FilmRecommender"]
users_collection = db["users"]

@pytest.fixture(scope="function")
def setup_test_user():
    """Crea un utente di test e lo elimina dopo il test."""
    username = "test_user"
    password = "secure_password"
    profile_pic = "profile_pic_url"

    # Pulisci eventuali dati esistenti
    users_collection.delete_one({"username": username})

    # Crea un nuovo utente
    register_user(username, password, profile_pic)

    yield username, password  # Restituisce i dati di test per il test

    # Cleanup dopo il test
    users_collection.delete_one({"username": username})


def test_register_user(setup_test_user):
    username, password = setup_test_user

    user = get_user(username)
    assert user is not None
    assert user["username"] == username
    assert "password_hash" in user


def test_authenticate_user(setup_test_user):
    username, password = setup_test_user

    authenticated, user = authenticate_user(username, password)
    assert authenticated is True
    assert user is not None
    assert user["username"] == username


def test_update_and_get_preferences(setup_test_user):
    username, _ = setup_test_user
    preferences = ["movie_1", "movie_2"]

    response = update_preferences(username, preferences)
    assert response == "Preferences updated successfully."

    saved_preferences = get_preferences(username)
    assert saved_preferences == preferences


def test_update_and_get_disliked(setup_test_user):
    username, _ = setup_test_user
    disliked = ["movie_3", "movie_4"]

    response = update_disliked(username, disliked)
    assert response == "Preferences updated successfully."

    saved_disliked = get_disliked(username)
    assert saved_disliked == disliked

import pytest
from unittest.mock import patch
from app import get_movie_poster

@patch("requests.get")
def test_get_movie_poster_success(mock_get):
    """Test per verificare il recupero del poster con una risposta valida."""
    # Mock della risposta API OMDB per il film
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "Response": "True",
        "Poster": "http://example.com/poster.jpg"
    }

    poster_url = get_movie_poster("Gladiator", 2000)

    # Verifica che l'URL del poster sia corretto
    assert poster_url == "http://example.com/poster.jpg"
    assert mock_get.call_count == 1  # Una chiamata all'API

@patch("requests.get")
def test_get_movie_poster_no_poster(mock_get):
    """Test per verificare il comportamento quando il poster non è disponibile."""
    # Mock della risposta API OMDB senza poster
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "Response": "True",
        "Poster": "N/A"
    }

    poster_url = get_movie_poster("Unknown Movie", 2000)

    # Verifica che il risultato sia None se il poster non è disponibile
    assert poster_url == "N/A"
    assert mock_get.call_count == 1

@patch("requests.get")
def test_get_movie_poster_api_error(mock_get):
    """Test per verificare il comportamento in caso di errore dell'API."""
    # Simula un errore di connessione
    mock_get.side_effect = Exception("API connection error")

    poster_url = get_movie_poster("Gladiator", 2000)

    # Verifica che il risultato sia None in caso di errore
    assert poster_url is None
    assert mock_get.call_count == 1
import pytest
import pandas as pd
import numpy as np
from src.knn_model import filter_movies, get_recommendations

def test_filter_movies():
    movies = pd.DataFrame({
        "filmtv_id": [1, 2, 3],
        "country": ["USA", "Italy", "France"],
        "directors": ["Dir1", "Dir2", "Dir3"],
        "actors": ["Act1", "Act2", "Act3"],
        "year": [2000, 2010, 2020],
        "total_votes": [100, 200, 300],
        "humor": [1, 2, 3],
        "weighted_rating": [7.0, 8.0, 9.0],
        "duration_log": [4.5, 5.0, 5.5],
        "genre_encoded": [1, 2, 3]
    })

    # Filtra per anno
    filtered = filter_movies(movies, start_year=2010)
    assert len(filtered) == 2
    assert all(filtered["year"] >= 2010)

    # Filtra per attore
    filtered = filter_movies(movies, actors="Act2")
    assert len(filtered) == 1
    assert filtered.iloc[0]["actors"] == "Act2"

    # Filtra per paese
    filtered = filter_movies(movies, genre=None, actors=None, directors=None, max_duration=None, start_year=None, end_year=None)
    assert len

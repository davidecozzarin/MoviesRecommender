import pandas as pd
from app import load_preprocessed_data, get_random_movies

def test_load_preprocessed_data():
    df = load_preprocessed_data("data/preprocessed_filmtv_movies.csv")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_get_random_movies():
    movies = pd.DataFrame({
        "filmtv_id": [1, 2, 3],
        "avg_vote": [7.6, 8.0, 7.5]
    })
    result = get_random_movies(movies, num_movies=2)
    assert isinstance(result, list)
    assert len(result) == 2

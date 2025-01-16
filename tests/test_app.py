import pandas as pd
import pytest
from src.movies_utils import load_preprocessed_data, get_random_movies

@pytest.fixture
def sample_movies_df():
    """Fixture per un DataFrame di esempio di film."""
    data = {
        "filmtv_id": [1, 2, 3, 4],
        "avg_vote": [7.6, 8.0, 7.5, 6.5],
        "title": ["Movie1", "Movie2", "Movie3", "Movie4"],
        "duration": [120, 150, 100, 90],
        "year": [2010, 2012, 2015, 2020],
    }
    return pd.DataFrame(data)

def test_load_preprocessed_data():
    """Test per verificare che il caricamento del file CSV funzioni correttamente."""
    df = load_preprocessed_data("data/preprocessed_filmtv_movies.csv")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "filmtv_id" in df.columns  # Controlla che una colonna chiave esista.

def test_load_preprocessed_data_error_handling():
    """Test per verificare che venga mostrato un errore con un file inesistente."""
    df = load_preprocessed_data("data/nonexistent_file.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.empty

def test_get_random_movies(sample_movies_df):
    """Test per verificare che vengano restituiti film casuali."""
    result = get_random_movies(sample_movies_df, num_movies=2)
    assert isinstance(result, list)
    assert len(result) == 2
    for movie in result:
        assert "filmtv_id" in movie  # Controlla che i film abbiano un ID.
        assert movie["avg_vote"] >= 7.5  # Controlla che rispettino il filtro.

def test_get_random_movies_not_enough_movies(sample_movies_df):
    """Test per verificare il comportamento con meno film disponibili del richiesto."""
    result = get_random_movies(sample_movies_df[sample_movies_df["avg_vote"] >= 7.5], num_movies=5)
    assert len(result) == 3  # Solo 3 film hanno avg_vote >= 7.5.

def test_get_random_movies_no_movies(sample_movies_df):
    """Test per verificare il comportamento quando non ci sono film disponibili."""
    result = get_random_movies(sample_movies_df[sample_movies_df["avg_vote"] >= 9], num_movies=2)
    assert len(result) == 0  # Nessun film rispetta il filtro.

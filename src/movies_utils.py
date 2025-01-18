import streamlit as st
import pandas as pd
import requests

def load_preprocessed_data(file_path):
    try:
        movies = pd.read_csv(file_path)
        return movies
    except Exception as e:
        st.error(f"Errore durante il caricamento dei dati: {e}")
        return pd.DataFrame()

def get_random_movies(movies_df, num_movies=30, min_avg_vote=7.5):  
    filtered_movies = movies_df[movies_df['avg_vote'] >= min_avg_vote]
    if len(filtered_movies) < num_movies:
        st.warning("Non ci sono abbastanza film con un punteggio medio sufficiente. Mostrando tutti i film disponibili.")
        num_movies = len(filtered_movies)
    return filtered_movies.sample(n=num_movies).to_dict(orient="records")

def get_movie_poster(title, year):
    """Recupera il poster di un film utilizzando l'API OMDb."""
    api_key = "f34d45dd"
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={title}&y={year}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("Response") == "True":
            return data.get("Poster")
        else:
            return None  # Nessun poster trovato
    except Exception as e:
        print(f"Errore durante il recupero del poster: {e}")
        return None

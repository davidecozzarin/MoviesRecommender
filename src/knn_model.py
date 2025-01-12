import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.compose import ColumnTransformer
import numpy as np
import os
from scipy.sparse import issparse

# Caricamento del dataset
current_dir = os.path.dirname(os.path.abspath(__file__))  # Directory corrente del file script
csv_path = os.path.join(current_dir, '..', 'data', 'preprocessed_filmtv_movies.csv') # Percorso relativo al file CSV

# Normalizza il percorso per garantire compatibilità cross-platform
csv_path = os.path.normpath(csv_path)

# Leggi il CSV usando pandas
df0 = pd.read_csv(csv_path) 
df1 = df0.copy()
df1 = df1.dropna()

# Colonne specifiche
SELECTED_COLUMNS = [
    'title', 'year', 'country', 'directors', 'actors', 'total_votes', 
    'humor', 'rhythm', 'effort', 'tension', 'erotism', 
    'weighted_rating', 'duration_log', 'genre_encoded'
]

# Filtrare le colonne
df = df1[SELECTED_COLUMNS]

# Dizionario dei pesi per le colonne numeriche
NUMERIC_COLUMN_WEIGHTS = {
    'year': 1.0,
    'total_votes': 1.2,
    'humor': 1.0,
    'rhythm': 1.0,
    'effort': 1.0,
    'tension': 1.0,
    'erotism': 1.0,
    'weighted_rating': 10.0,
    'duration_log': 1.0,
    'genre_encoded': 2.0
}

# Dizionario dei pesi per le colonne testuali
TEXT_COLUMN_WEIGHTS = {
    'country': 0.8,
    'directors': 1.2,
    'actors': 1.0
}

# Pre-elaborazione
def preprocess_dataset(df):
    # Prepara il trasformatore per le feature
    column_transformer = ColumnTransformer([
        ('tfidf_country', TfidfVectorizer(max_features=5000, min_df=2, max_df=0.8), 'country'),
        ('tfidf_directors', TfidfVectorizer(max_features=5000, min_df=2, max_df=0.8), 'directors'),
        ('tfidf_actors', TfidfVectorizer(max_features=5000, min_df=2, max_df=0.8), 'actors'),
        ('scaler_numeric', StandardScaler(), list(NUMERIC_COLUMN_WEIGHTS.keys())),
    ], remainder='drop')

    # Applica il trasformatore senza convertire in array denso
    transformed_data = column_transformer.fit_transform(df)

    # Applica i pesi alle colonne testuali e numeriche
    if issparse(transformed_data):
        transformed_data = transformed_data.toarray()

    # Identifica gli indici per i pesi testuali e numerici
    start_idx = 0
    for col, weight in TEXT_COLUMN_WEIGHTS.items():
        end_idx = start_idx + column_transformer.transformers_[list(TEXT_COLUMN_WEIGHTS.keys()).index(col)][1].vocabulary_.__len__()
        transformed_data[:, start_idx:end_idx] *= weight
        start_idx = end_idx

    numeric_indices = slice(-len(NUMERIC_COLUMN_WEIGHTS), None)  # Ultime colonne trasformate sono quelle numeriche
    transformed_data[:, numeric_indices] *= np.array(list(NUMERIC_COLUMN_WEIGHTS.values()))

    return transformed_data, column_transformer

transformed_data, column_transformer = preprocess_dataset(df)

# Costruzione del modello kNN
knn_model = NearestNeighbors(n_neighbors=20, metric='euclidean')  # Puoi cambiare la metrica n_neighbors in base a quante raccomandazioni si vuole fare
knn_model.fit(transformed_data)

# Funzione per calcolare raccomandazioni
def recommend_movies(user_liked_movies, user_disliked_movies, df, column_transformer):
    print("Finding recommendations...")

    # Rimuovi i film scelti dall'utente (sia apprezzati che non apprezzati) dal dataset considerato
    filtered_df = df[~df['title'].isin(user_liked_movies + user_disliked_movies)]

    # Estrai le feature dei film apprezzati
    liked_data = df[df['title'].isin(user_liked_movies)]
    liked_transformed = column_transformer.transform(liked_data)

    # Estrai le feature dei film non apprezzati
    disliked_data = df[df['title'].isin(user_disliked_movies)]
    disliked_transformed = column_transformer.transform(disliked_data)

    # Se sono matrici sparse, convertili in array densi
    if issparse(liked_transformed):
        liked_transformed = liked_transformed.toarray()
    if issparse(disliked_transformed):
        disliked_transformed = disliked_transformed.toarray()

    # Calcola i centroidi (media delle feature dei film scelti)
    user_liked_profile = np.mean(liked_transformed, axis=0) if len(user_liked_movies) > 0 else np.zeros(liked_transformed.shape[1])
    user_disliked_profile = np.mean(disliked_transformed, axis=0) if len(user_disliked_movies) > 0 else np.zeros(disliked_transformed.shape[1])

    # Combina i centroidi per creare un profilo utente finale
    user_profile = user_liked_profile - user_disliked_profile  # Penalizza le zone dei film non graditi
    user_profile = user_profile.reshape(1, -1)  # Assicurati che sia 2D

    # Ricalcola i vicini escludendo i film scelti
    filtered_transformed = column_transformer.transform(filtered_df)
    if issparse(filtered_transformed):
        filtered_transformed = filtered_transformed.toarray()

    # Trova i vicini più vicini
    _, indices = knn_model.kneighbors(user_profile)

    # Ritorna i titoli dei film raccomandati
    recommended_movies = filtered_df.iloc[indices[0]]['title'].values
    return recommended_movies


def filter_movies(dataset, genre=None, max_duration=None, actors=None, directors=None, start_year=None, end_year=None):
    """
    Filters the movies dataset based on user inputs.
    
    Parameters:
        dataset (DataFrame): The dataset of movies.
        genre (str): Filter movies by genre.
        max_duration (int): Maximum duration of movies.
        actors (str): Filter movies by actor name (partial or full match).
        directors (str): Filter movies by director name (partial or full match).
        start_year (int): Start year for filtering movies (inclusive).
        end_year (int): End year for filtering movies (inclusive).
    
    Returns:
        DataFrame: Filtered dataset based on the given parameters.
    """
    filtered = dataset.copy()

    # Filter by genre
    if genre:
        filtered = filtered[filtered['genre'].str.contains('|'.join(genre), case=False, na=False)]

    # Filter by duration
    if max_duration is not None:
        filtered = filtered[filtered['duration'] <= max_duration]

    # Filter by actors
    if actors:
        filtered = filtered[filtered['actors'].str.contains(actors, case=False, na=False)]

    # Filter by directors
    if directors:
        filtered = filtered[filtered['directors'].str.contains(directors, case=False, na=False)]

    # Filter by year
    if start_year is not None:
        filtered = filtered[filtered['year'] >= start_year]
    if end_year is not None:
        filtered = filtered[filtered['year'] <= end_year]

    return filtered

def get_recommendations(user_liked_movies, user_disliked_movies, filters):
    """
    Restituisce raccomandazioni basate sui film apprezzati, non apprezzati e filtri.
    
    Args:
        user_liked_movies (list): Lista di titoli di film apprezzati.
        user_disliked_movies (list): Lista di titoli di film non apprezzati.
        filters (dict): Filtri selezionati dall'utente.
            - 'genre': lista di generi selezionati
            - 'duration_range': tuple (min_duration, max_duration)
            - 'actor': stringa per filtrare per attore
            - 'director': stringa per filtrare per regista
            - 'year_range': tuple (min_year, max_year)
            
    Returns:
        list: Lista di titoli raccomandati.
    """
    # Caricamento del dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, '..', 'data', 'preprocessed_filmtv_movies.csv')
    df = pd.read_csv(csv_path).dropna()

    # Applica il filtraggio utilizzando filter_movies
    df = filter_movies(
        dataset=df,
        genre=filters.get("genre"),
        max_duration=filters.get("duration_range", (None, None))[1],
        actors=filters.get("actor"),
        directors=filters.get("director"),
        start_year=filters.get("year_range", (None, None))[0],
        end_year=filters.get("year_range", (None, None))[1]
    )

    # Debugging output
    print(f"Number of movies after filtering: {len(df)}")
    if df.empty:
        print("Filtered dataset is empty. Check the filters.")
        return []

    # Pre-elaborazione e raccomandazione
    transformed_data, column_transformer = preprocess_dataset(df)
    knn_model = NearestNeighbors(n_neighbors=20, metric='euclidean')
    knn_model.fit(transformed_data)

    # Rimuovi i film scelti dall'utente
    filtered_df = df[~df['title'].isin(user_liked_movies + user_disliked_movies)]

    # Controllo per dati vuoti
    if filtered_df.empty:
        return []

    # Profilo utente
    liked_data = df[df['title'].isin(user_liked_movies)]
    if liked_data.empty:
        raise ValueError("No liked movies found in the dataset. Cannot generate recommendations.")

    liked_transformed = column_transformer.transform(liked_data)
    if issparse(liked_transformed):
        liked_transformed = liked_transformed.toarray()
    user_liked_profile = np.mean(liked_transformed, axis=0)

    user_disliked_profile = np.zeros(user_liked_profile.shape)
    if user_disliked_movies:
        disliked_data = df[df['title'].isin(user_disliked_movies)]
        if not disliked_data.empty:
            disliked_transformed = column_transformer.transform(disliked_data)
            if issparse(disliked_transformed):
                disliked_transformed = disliked_transformed.toarray()
            user_disliked_profile = np.mean(disliked_transformed, axis=0)

    user_profile = user_liked_profile - user_disliked_profile
    user_profile = user_profile.reshape(1, -1)

    filtered_transformed = column_transformer.transform(filtered_df)
    if issparse(filtered_transformed):
        filtered_transformed = filtered_transformed.toarray()

    _, indices = knn_model.kneighbors(user_profile)
    recommended_movies = filtered_df.iloc[indices[0]]['title'].values
    return recommended_movies


"""
# Esempio di utilizzo
user_liked_movies = ['Inception', 'The Matrix', 'The Shining']
user_disliked_movies = ['Twilight', 'Fifty Shades of Grey']
recommendations = recommend_movies(user_liked_movies, user_disliked_movies, df, column_transformer)
print("Film recommendations:", recommendations)
print("Film scelti:")
print(df1[df1['title'].isin(user_liked_movies)])
print(df1[df1['title'].isin(user_disliked_movies)])
print("Film raccomandati:")
print(df1[df1['title'].isin(recommendations)])
"""
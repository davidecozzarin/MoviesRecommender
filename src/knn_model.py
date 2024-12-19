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
df1 = pd.read_csv(csv_path) # Dataset con le colonne: 'title', 'year', 'genre', 'duration', 'country', 'directors', 'actors', 'avg_vote', 'total_votes', 'humor', 'rhythm', 'effort', 'tension', 'erotism', 'weighted_rating', 'duration_category'
df = df1.copy()
df = df.dropna()

# Dizionario dei pesi per le colonne numeriche
NUMERIC_COLUMN_WEIGHTS = {
    'year': 2.0,
    'duration': 1.0,
    'avg_vote': 1.5,
    'total_votes': 1.2,
    'humor': 1.0,
    'rhythm': 1.0,
    'effort': 1.0,
    'tension': 1.0,
    'erotism': 1.0,
    'weighted_rating': 2.0
}

# Dizionario dei pesi per le colonne testuali
TEXT_COLUMN_WEIGHTS = {
    'genre': 2.0,
    'country': 0.8,
    'directors': 1.2,
    'actors': 1.0
}

# Pre-elaborazione
def preprocess_dataset(df):
    # Prepara il trasformatore per le feature
    column_transformer = ColumnTransformer([
        ('tfidf_genre', TfidfVectorizer(max_features=5000, min_df=2, max_df=0.8), 'genre'),
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
knn_model = NearestNeighbors(n_neighbors=20, metric='euclidean')  # Puoi cambiare la metrica in base al caso
knn_model.fit(transformed_data)

# Funzione per calcolare raccomandazioni
def recommend_movies(user_selected_movies, df, column_transformer, n_recommendations=20):
    print("Finding recommendations...")

    # Rimuovi i film scelti dall'utente dal dataset considerato
    filtered_df = df[~df['title'].isin(user_selected_movies)]

    # Estrai le feature dei film scelti dall'utente
    user_data = df[df['title'].isin(user_selected_movies)]
    user_transformed = column_transformer.transform(user_data)

    # Se è una matrice sparsa, convertila in un array denso
    if issparse(user_transformed):
        user_transformed = user_transformed.toarray()

    # Calcola il centroide (media delle feature dei film scelti)
    user_profile = np.mean(user_transformed, axis=0).reshape(1, -1)  # Assicurati che sia 2D

    # Ricalcola i vicini escludendo i film scelti
    filtered_transformed = column_transformer.transform(filtered_df)
    if issparse(filtered_transformed):
        filtered_transformed = filtered_transformed.toarray()

    # Applica i pesi alle colonne testuali
    start_idx = 0
    for col, weight in TEXT_COLUMN_WEIGHTS.items():
        end_idx = start_idx + column_transformer.transformers_[list(TEXT_COLUMN_WEIGHTS.keys()).index(col)][1].vocabulary_.__len__()
        filtered_transformed[:, start_idx:end_idx] *= weight
        start_idx = end_idx

    # Applica i pesi alle colonne numeriche
    numeric_indices = slice(-len(NUMERIC_COLUMN_WEIGHTS), None)
    filtered_transformed[:, numeric_indices] *= np.array(list(NUMERIC_COLUMN_WEIGHTS.values()))

    # Allena temporaneamente un nuovo modello sui dati filtrati
    temp_knn_model = NearestNeighbors(n_neighbors=n_recommendations, metric='euclidean')
    temp_knn_model.fit(filtered_transformed)

    # Trova i vicini più vicini
    _, indices = temp_knn_model.kneighbors(user_profile, n_neighbors=n_recommendations)

    # Ritorna i titoli dei film raccomandati
    recommended_movies = filtered_df.iloc[indices[0]]['title'].values
    return recommended_movies

# Esempio di utilizzo
user_selected_movies = ['Inception', 'The Matrix', 'The Shining']  # Film scelti dall'utente
recommendations = recommend_movies(user_selected_movies, df, column_transformer)
print("Film recommendations:", recommendations)
print("Film scelti:")
print(df[df['title'].isin(user_selected_movies)])
print("Film raccomandati:")
print(df[df['title'].isin(recommendations)])
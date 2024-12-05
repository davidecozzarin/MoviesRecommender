import pandas as pd

def load_and_preprocess_data(file_path):
    # Carica il file CSV
    data = pd.read_csv(file_path)

    # Seleziona le colonne utili
    movies = data[['title', 'year', 'genre', 'duration', 'directors', 'actors', 'avg_vote', 'description']]

    # Gestione dei valori mancanti
    movies.fillna({'genre': 'Unknown', 'directors': 'Unknown', 'actors': 'Unknown', 'description': ''}, inplace=True)

    # Converte colonne come 'genre' e 'actors' in liste
    movies['genre'] = movies['genre'].str.split(', ')
    movies['actors'] = movies['actors'].str.split(', ')

    # Crea un campo combinato per il motore di raccomandazione
    movies['combined_features'] = (
        movies['genre'].apply(lambda x: ' '.join(x) if isinstance(x, list) else x) + ' ' +
        movies['directors'] + ' ' +
        movies['actors'].apply(lambda x: ' '.join(x) if isinstance(x, list) else x) + ' ' +
        movies['description']
    )

    return movies

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.compose import ColumnTransformer
import numpy as np
import os
from scipy.sparse import issparse

current_dir = os.path.dirname(os.path.abspath(__file__))  # Directory corrente del file script
csv_path = os.path.join(current_dir, '..', 'data', 'preprocessed_filmtv_movies.csv') # Percorso relativo al file CSV

csv_path = os.path.normpath(csv_path)

df0 = pd.read_csv(csv_path) 
df1 = df0.copy()
df1 = df1.dropna()

SELECTED_COLUMNS = [
    'title', 'year', 'country', 'directors', 'actors', 'total_votes', 
    'humor', 'rhythm', 'effort', 'tension', 'erotism', 
    'weighted_rating', 'duration_log', 'genre_encoded'
]

df = df1[SELECTED_COLUMNS]

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

TEXT_COLUMN_WEIGHTS = {
    'country': 0.8,
    'directors': 1.2,
    'actors': 1.0
}

def preprocess_dataset(df):
    column_transformer = ColumnTransformer([
        ('tfidf_country', TfidfVectorizer(max_features=5000, min_df=2, max_df=0.8), 'country'),
        ('tfidf_directors', TfidfVectorizer(max_features=5000, min_df=2, max_df=0.8), 'directors'),
        ('tfidf_actors', TfidfVectorizer(max_features=5000, min_df=2, max_df=0.8), 'actors'),
        ('scaler_numeric', StandardScaler(), list(NUMERIC_COLUMN_WEIGHTS.keys())),
    ], remainder='drop')

    transformed_data = column_transformer.fit_transform(df)

    if issparse(transformed_data):
        transformed_data = transformed_data.toarray()

    start_idx = 0
    for col, weight in TEXT_COLUMN_WEIGHTS.items():
        end_idx = start_idx + column_transformer.transformers_[list(TEXT_COLUMN_WEIGHTS.keys()).index(col)][1].vocabulary_.__len__()
        transformed_data[:, start_idx:end_idx] *= weight
        start_idx = end_idx

    numeric_indices = slice(-len(NUMERIC_COLUMN_WEIGHTS), None)
    transformed_data[:, numeric_indices] *= np.array(list(NUMERIC_COLUMN_WEIGHTS.values()))

    return transformed_data, column_transformer


def filter_movies(dataset, genre=None, max_duration=None, actors=None, directors=None, start_year=None, end_year=None):

    filtered = dataset.copy()

    if genre:
        filtered = filtered[filtered['genre'].str.contains('|'.join(genre), case=False, na=False)]

    if max_duration is not None:
        filtered = filtered[filtered['duration'] <= max_duration]

    if actors:
        filtered = filtered[filtered['actors'].str.contains(actors, case=False, na=False)]

    if directors:
        filtered = filtered[filtered['directors'].str.contains(directors, case=False, na=False)]

    if start_year is not None:
        filtered = filtered[filtered['year'] >= start_year]
    if end_year is not None:
        filtered = filtered[filtered['year'] <= end_year]

    return filtered

def get_recommendations(user_liked_movies_ids, user_disliked_movies_ids, filters):

    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, '..', 'data', 'preprocessed_filmtv_movies.csv')
    df = pd.read_csv(csv_path).dropna()

    filtered_df = filter_movies(
        dataset=df,
        genre=filters.get("genre"),
        max_duration=filters.get("duration_range", (None, None))[1],
        actors=filters.get("actor"),
        directors=filters.get("director"),
        start_year=filters.get("year_range", (None, None))[0],
        end_year=filters.get("year_range", (None, None))[1]
    )

    print(f"Number of movies after filtering: {len(filtered_df)}")
    if filtered_df.empty:
        print("Filtered dataset is empty. Check the filters.")
        return []

    filtered_df = filtered_df[
        ~filtered_df['filmtv_id'].isin(user_liked_movies_ids + user_disliked_movies_ids)
    ]

    if filtered_df.empty:
        print("Filtered dataset is empty after removing liked and disliked movies.")
        return []

    liked_data = df[df['filmtv_id'].isin(user_liked_movies_ids)]
    disliked_data = df[df['filmtv_id'].isin(user_disliked_movies_ids)]

    if liked_data.empty:
        raise ValueError("No liked movies found in the dataset. Cannot generate recommendations.")

    transformed_data, column_transformer = preprocess_dataset(filtered_df)
    liked_transformed = column_transformer.transform(liked_data)
    if issparse(liked_transformed):
        liked_transformed = liked_transformed.toarray()
    user_liked_profile = np.mean(liked_transformed, axis=0)

    if not disliked_data.empty:
        disliked_transformed = column_transformer.transform(disliked_data)
        if issparse(disliked_transformed):
            disliked_transformed = disliked_transformed.toarray()
        user_disliked_profile = np.mean(disliked_transformed, axis=0)
    else:
        user_disliked_profile = np.zeros(user_liked_profile.shape)

    user_profile = user_liked_profile - user_disliked_profile
    user_profile = user_profile.reshape(1, -1)

    filtered_transformed = column_transformer.transform(filtered_df)
    if issparse(filtered_transformed):
        filtered_transformed = filtered_transformed.toarray()

    knn_model = NearestNeighbors(n_neighbors=20, metric='euclidean')
    knn_model.fit(filtered_transformed)
    _, indices = knn_model.kneighbors(user_profile)

    recommended_movies_ids = filtered_df.iloc[indices[0]]['filmtv_id'].values
    return recommended_movies_ids


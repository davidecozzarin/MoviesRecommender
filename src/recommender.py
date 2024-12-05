import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def create_similarity_matrix(movies):
    # Crea un vettore TF-IDF
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies['combined_features'])

    # Calcola la similarità coseno
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def recommend_movies(title, movies, cosine_sim):
    # Mappa titolo -> indice
    title_to_index = pd.Series(movies.index, index=movies['title'])

    # Ottieni l'indice del film dato
    idx = title_to_index.get(title)
    if idx is None:
        return "Film non trovato nel database."

    # Ottieni i punteggi di similarità
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Seleziona i top 10 film simili
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]

    return movies.iloc[movie_indices][['title', 'year', 'genre', 'avg_vote']]

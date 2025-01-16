import streamlit as st
from src.movies_utils import load_preprocessed_data
from src.knn_model import get_recommendations
from src.auth import get_disliked, get_preferences, get_user

def show_filters_page():
    st.header("Search for Movie Recommendations")

    # Carica il dataset
    movies = load_preprocessed_data("data/preprocessed_filmtv_movies.csv")

    # Filtri opzionali al centro
    st.markdown("### Filter Options")
    selected_genre = st.multiselect("Select Genre", options=movies['genre'].unique())
    duration_range = st.slider("Select Duration (minutes)", int(movies['duration'].min()), int(movies['duration'].max()), (60, 120))
    selected_actor = st.text_input("Search by Actor")
    selected_director = st.text_input("Search by Director")
    year_range = st.slider("Select Year Range", int(movies['year'].min()), int(movies['year'].max()), (2000, 2020))

    # Bottone per la raccomandazione
    if st.button("Get Recommandations"):
        filters = {
            "genre": selected_genre,
            "duration_range": duration_range,
            "actor": selected_actor.strip(),
            "director": selected_director.strip(),
            "year_range": year_range,
        }

        print(f"Filters applied for the reccomandation: {filters}")

        # Recupera le informazioni dell'utente dal database
        user_info = get_user(st.session_state["username"])
        preferences_ids = get_preferences(st.session_state["username"])
        disliked_ids = get_disliked(st.session_state["username"])

        recommendations = get_recommendations(preferences_ids, disliked_ids, filters)

        if len(recommendations) > 0:  # Verifica se ci sono risultati
            st.session_state["recommendations"] = recommendations
            st.session_state["page"] = "results"
            st.rerun()
        else:
            st.warning("No recommendations found based on your preferences and filters.")
        
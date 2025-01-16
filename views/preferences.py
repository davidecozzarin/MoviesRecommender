import streamlit as st
from src.movies_utils import load_preprocessed_data
from src.auth import get_preferences, get_disliked, update_preferences, update_disliked

def show_preferences_page():
    st.header("Your Saved Preferences and Disliked Movies")

    # Recupera i film salvati dall'utente
    preferences = get_preferences(st.session_state["username"])
    disliked = get_disliked(st.session_state["username"])
    movies = load_preprocessed_data("data/preprocessed_filmtv_movies.csv")

    # Film nelle preferenze
    if preferences:
        st.subheader("Liked Movies")
        liked_movies = movies[movies['filmtv_id'].isin(preferences)]  # Filtra i film salvati
        for _, movie in liked_movies.iterrows():
            col1, col2, col3 = st.columns([9, 1, 1])
            with col1:
                st.write(f"**Title**: {movie['title']} | **Duration**: {movie['duration']} min | **Year**: {movie['year']}")
            with col2:
                if st.button("🔍", key=f"details_{movie['filmtv_id']}", help="View details of this movie", use_container_width=True):
                    # Passa alla pagina dei dettagli
                    st.session_state["page"] = "details"
                    st.session_state["movie_details"] = movie.to_dict()  # Salva i dettagli del film scelto
                    st.rerun()
            with col3:
                if st.button("❌", key=f"remove_like_{movie['filmtv_id']}", help="Remove this movie", use_container_width=True):
                    if(len(preferences) < 4):
                        with col1:
                            st.error("Keep at least three liked movies in the list.")
                    else:
                        preferences.remove(movie['filmtv_id'])                    
                        update_preferences(st.session_state["username"], preferences)
                        st.rerun()
    else:
        st.warning("No liked movies found.")

    # Film nei dislike
    if disliked:
        st.subheader("Disliked Movies")
        disliked_movies = movies[movies['filmtv_id'].isin(disliked)]  # Filtra i film salvati nei dislike
        for _, movie in disliked_movies.iterrows():
            col1, col2, col3 = st.columns([9, 1, 1])
            with col1:
                st.write(f"**Title**: {movie['title']} | **Duration**: {movie['duration']} min | **Year**: {movie['year']}")
            with col2:
                if st.button("🔍", key=f"details_disliked_{movie['filmtv_id']}", help="View details of this movie", use_container_width=True):
                    # Passa alla pagina dei dettagli
                    st.session_state["page"] = "details"
                    st.session_state["movie_details"] = movie.to_dict()  
                    st.rerun()
            with col3:
                if st.button("❌", key=f"remove_dislike_{movie['filmtv_id']}", help="Remove this movie", use_container_width=True):
                    if(len(preferences) < 4):
                        with col1:
                            st.error("Keep at least three liked movies in the list.")
                    else:
                        disliked.remove(movie['filmtv_id'])
                        update_disliked(st.session_state["username"], disliked)
                        st.rerun()
    else:
        st.warning("No disliked movies found.")
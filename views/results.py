import streamlit as st
from src.movies_utils import load_preprocessed_data
from src.auth import get_preferences, get_disliked, update_preferences, update_disliked

def show_results_page():
    st.header("Recommended Movies")
    # Recupera le raccomandazioni salvate nello stato della sessione
    recommendations = st.session_state.get("recommendations", [])

    if len(recommendations) > 0:
        # Carica il dataset per ottenere i dettagli dei film raccomandati
        movies = load_preprocessed_data("data/preprocessed_filmtv_movies.csv")
        
        # Filtra i film raccomandati utilizzando il loro filmtv_id
        recommended_movies = movies[movies['filmtv_id'].isin(recommendations)]
        
        # Mostra i risultati
        for _, movie in recommended_movies.iterrows():
            col1, col2, col3, col4 = st.columns([8, 1, 1, 1])  # Layout: Film info, Like button, Dislike button
            with col1:
                st.write(f"**Title**: {movie['title']} | **Duration**: {movie['duration']} min | **Year**: {movie['year']}")

            preferences = get_preferences(st.session_state["username"])
            disliked = get_disliked(st.session_state["username"])
            # Icone Material Symbols per like/dislike
            like_icon = "❤️" if movie['filmtv_id'] in preferences else ":material/thumb_up:"
            dislike_icon = "🤢" if movie['filmtv_id'] in disliked else ":material/thumb_down_off_alt:"

            with col2:
                if st.button("🔍", key=f"details_{movie['filmtv_id']}", help="View details of this movie", use_container_width=True):
                    # Passa alla pagina dei dettagli
                    st.session_state["from_page"] = "results"
                    st.session_state["page"] = "result_details"
                    st.session_state["movie_details"] = movie.to_dict()  # Salva i dettagli del film scelto
                    st.rerun()

            with col3:
                if st.button(f"{like_icon}", key=f"like_{movie['filmtv_id']}", help="Like this movie", use_container_width=True):
                    # Aggiorna preferenze (like)
                    preferences = get_preferences(st.session_state["username"])
                    disliked = get_disliked(st.session_state["username"])

                    if movie['filmtv_id'] not in preferences:
                        preferences.append(movie['filmtv_id'])
                        update_preferences(st.session_state["username"], preferences)
                    
                    # Rimuovi da disliked se presente
                    if movie['filmtv_id'] in disliked:
                        disliked.remove(movie['filmtv_id'])
                        update_disliked(st.session_state["username"], disliked) 
                    st.rerun()

            with col4:
                if st.button(f"{dislike_icon}", key=f"dislike_{movie['filmtv_id']}", help="Dislike this movie", use_container_width=True):
                    # Aggiorna dislike
                    disliked = get_disliked(st.session_state["username"])
                    preferences = get_preferences(st.session_state["username"])
                    
                    if movie['filmtv_id'] not in disliked:
                        disliked.append(movie['filmtv_id'])
                        update_disliked(st.session_state["username"], disliked)
                    
                    # Rimuovi da preferences se presente
                    if movie['filmtv_id'] in preferences:
                        preferences.remove(movie['filmtv_id'])
                        update_preferences(st.session_state["username"], preferences)
                    st.rerun()
                    
    else:
        st.warning("No recommendations found based on your preferences and filters.")

    if st.button("Back"):
        st.session_state["page"] = "filters"
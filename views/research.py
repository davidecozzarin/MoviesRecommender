import streamlit as st
import math
from src.movies_utils import load_preprocessed_data
from src.auth import get_disliked, get_preferences, get_user, update_disliked, update_preferences
from src.filtering_functions import filter_movies

def show_research_page():
    st.header("Search for a Particular Movie")

    # Carica il dataset
    movies = load_preprocessed_data("data/preprocessed_filmtv_movies.csv")

    # Filtri al centro
    st.markdown("### Filter Options")
    selected_title = st.text_input("Search by Title")
    selected_genre = st.multiselect("Select Genre", options=movies['genre'].unique())
    duration_range = st.slider("Select Duration (minutes)", int(movies['duration'].min()), int(movies['duration'].max()), (60, 120))
    selected_actor = st.text_input("Search by Actor")
    selected_director = st.text_input("Search by Director")
    year_range = st.slider("Select Year Range", int(movies['year'].min()), int(movies['year'].max()), (2000, 2020))

    # Bottone per la ricerca
    if st.button("Search"):
        filters = {
            "title": selected_title.strip(),
            "genre": selected_genre,
            "duration_range": duration_range,
            "actor": selected_actor.strip(),
            "director": selected_director.strip(),
            "year_range": year_range,
        }

        print(f"Filters applied for the research: {filters}")

        # Recupera le informazioni dell'utente dal database
        user_info = get_user(st.session_state["username"])
        preferences_ids = get_preferences(st.session_state["username"])
        disliked_ids = get_disliked(st.session_state["username"])

        results = filter_movies(movies, 
                        title=selected_title, 
                        genre=selected_genre, 
                        min_duration=duration_range[0], 
                        max_duration=duration_range[1], 
                        actors=selected_actor, 
                        directors=selected_director, 
                        start_year=year_range[0], 
                        end_year=year_range[1])
        
        print("Number of movies after filtering: ", len(results))

        if results.empty:
            st.warning("No movies found based on selected filters.")
        else:
            st.session_state["results"] = results['filmtv_id'].tolist()
            st.session_state["page"] = "research_results"
        st.rerun()

def show_research_results_page():
    st.header("Movies found")
    # Recupera le raccomandazioni salvate nello stato della sessione
    results = st.session_state.get("results", [])

    MOVIES_PER_PAGE = 30

    if len(results) > 0:
        # Carica il dataset per ottenere i dettagli dei film raccomandati
        movies = load_preprocessed_data("data/preprocessed_filmtv_movies.csv")
        
        # Filtra i film raccomandati utilizzando il loro filmtv_id
        movies_found = movies[movies['filmtv_id'].isin(results)]

        # Calcola il numero totale di pagine
        total_pages = math.ceil(len(movies_found) / MOVIES_PER_PAGE)

        # Inizializza la pagina corrente se non è già impostata
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = 1

        # Garantisce che la pagina corrente non superi i limiti
        st.session_state["current_page"] = max(1, min(st.session_state["current_page"], total_pages))

        # Mostra i film della pagina corrente
        start_idx = (st.session_state["current_page"] - 1) * MOVIES_PER_PAGE
        end_idx = start_idx + MOVIES_PER_PAGE

        # Estrai solo i film della pagina corrente
        current_movies = movies_found.iloc[start_idx:end_idx]

        if(total_pages > 1):
            # Visualizza i film della pagina corrent
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.markdown(
                    f"<p style='text-align: center;'>Page {st.session_state['current_page']} of {total_pages}</p>",
                    unsafe_allow_html=True
                )

        # Mostra i risultati
        for _, movie in current_movies.iterrows():
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
                    st.session_state["page"] = "result_details"
                    st.session_state["movie_details"] = movie.to_dict()  # Salva i dettagli del film scelto
                    st.session_state["from_page"] = "research_results"
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

        if(total_pages > 1):

            # Navigazione tra le pagine
            st.write("----")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.markdown(
                    f"<p style='text-align: center;'>Page {st.session_state['current_page']} of {total_pages}</p>",
                    unsafe_allow_html=True
                )

            # Barra di navigazione
            pagination_cols = st.columns(11)  # Totale colonne: 2 per ⏮️ e ◀️, 7 per numeri, 2 per ▶️ e ⏭️

            # Calcolo range delle pagine da mostrare (centrando quella corrente)
            half_range = 3  # Numero di pagine a sinistra e a destra della corrente
            min_page = max(1, st.session_state["current_page"] - half_range)
            max_page = min(total_pages, st.session_state["current_page"] + half_range)

            # Se ci sono meno di 7 pagine vicine disponibili, ribilancia a sinistra o a destra
            if max_page - min_page < 6:
                if min_page == 1:
                    max_page = min(7, total_pages)
                elif max_page == total_pages:
                    min_page = max(1, total_pages - 6)

            # Pulsante "⏮️" per andare alla prima pagina
            with pagination_cols[0]:
                if st.button("⏮️", disabled=st.session_state["current_page"] == 1):
                    st.session_state["current_page"] = 1
                    st.rerun()

            # Pulsante "◀️" per andare alla pagina precedente
            with pagination_cols[1]:
                if st.button("◀️", disabled=st.session_state["current_page"] == 1):
                    st.session_state["current_page"] -= 1
                    st.rerun()

            # Bottoni numerici per le pagine vicine
            for idx, page_num in enumerate(range(min_page, max_page + 1)):
                with pagination_cols[2 + idx]:  # Inizia dalla terza colonna
                    if st.button(
                        f"{page_num}",
                        key=f"page_{page_num}",
                        use_container_width=True,
                        disabled=(page_num == st.session_state["current_page"]),  # Disabilita il pulsante della pagina corrente
                    ):
                        st.session_state["current_page"] = page_num
                        st.rerun()

            # Pulsante "▶️" per andare alla pagina successiva
            with pagination_cols[9]:  # Penultima colonna
                if st.button("▶️", disabled=st.session_state["current_page"] == total_pages):
                    st.session_state["current_page"] += 1
                    st.rerun()

            # Pulsante "⏭️" per andare all'ultima pagina
            with pagination_cols[10]:  # Ultima colonna
                if st.button("⏭️", disabled=st.session_state["current_page"] == total_pages):
                    st.session_state["current_page"] = total_pages
                    st.rerun()
                    
    else:
        st.warning("No movies found based on selected filters.")

    if st.button("Back"):
        st.session_state["page"] = "research"
        st.rerun()
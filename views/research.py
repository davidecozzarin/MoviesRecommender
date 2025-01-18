import streamlit as st
import math
from src.movies_utils import load_preprocessed_data
from src.auth import get_disliked, get_preferences, get_user, update_disliked, update_preferences
from src.filtering_functions import filter_movies

def show_research_page():
    st.header("Search for a Particular Movie")

    movies = load_preprocessed_data("data/preprocessed_filmtv_movies.csv")

    st.markdown("### Filter Options")
    selected_title = st.text_input("Search by Title")
    selected_genre = st.multiselect("Select Genre", options=movies['genre'].unique())
    duration_range = st.slider("Select Duration (minutes)", int(movies['duration'].min()), int(movies['duration'].max()), (60, 120))
    selected_actor = st.text_input("Search by Actor")
    selected_director = st.text_input("Search by Director")
    year_range = st.slider("Select Year Range", int(movies['year'].min()), int(movies['year'].max()), (2000, 2020))

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
            st.session_state["current_page"] = 1
            st.session_state["results"] = results['filmtv_id'].tolist()
            st.session_state["page"] = "research_results"
            st.rerun()

def show_research_results_page():
    st.header("Movies found")
    results = st.session_state.get("results", [])

    MOVIES_PER_PAGE = 30

    if len(results) > 0:

        movies = load_preprocessed_data("data/preprocessed_filmtv_movies.csv")
        
        movies_found = movies[movies['filmtv_id'].isin(results)]

        total_pages = math.ceil(len(movies_found) / MOVIES_PER_PAGE)

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = 1

        st.session_state["current_page"] = max(1, min(st.session_state["current_page"], total_pages))

        start_idx = (st.session_state["current_page"] - 1) * MOVIES_PER_PAGE
        end_idx = start_idx + MOVIES_PER_PAGE

        current_movies = movies_found.iloc[start_idx:end_idx]

        if(total_pages > 1):
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

            like_icon = "❤️" if movie['filmtv_id'] in preferences else ":material/thumb_up:"
            dislike_icon = "🤢" if movie['filmtv_id'] in disliked else ":material/thumb_down_off_alt:"

            with col2:
                if st.button("🔍", key=f"details_{movie['filmtv_id']}", help="View details of this movie", use_container_width=True):
                    st.session_state["page"] = "result_details"
                    st.session_state["movie_details"] = movie.to_dict()  # Salva i dettagli del film scelto
                    st.session_state["from_page"] = "research_results"
                    st.rerun()

            with col3:
                if st.button(f"{like_icon}", key=f"like_{movie['filmtv_id']}", help="Like this movie", use_container_width=True):
                    preferences = get_preferences(st.session_state["username"])
                    disliked = get_disliked(st.session_state["username"])

                    if movie['filmtv_id'] not in preferences:
                        preferences.append(movie['filmtv_id'])
                        update_preferences(st.session_state["username"], preferences)
                    
                    if movie['filmtv_id'] in disliked:
                        disliked.remove(movie['filmtv_id'])
                        update_disliked(st.session_state["username"], disliked) 
                    st.rerun()

            with col4:
                if st.button(f"{dislike_icon}", key=f"dislike_{movie['filmtv_id']}", help="Dislike this movie", use_container_width=True):
                    disliked = get_disliked(st.session_state["username"])
                    preferences = get_preferences(st.session_state["username"])
                    
                    if movie['filmtv_id'] not in disliked:
                        disliked.append(movie['filmtv_id'])
                        update_disliked(st.session_state["username"], disliked)
                    
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
            pagination_cols = st.columns(11)


            half_range = 3  # Numero di pagine a sinistra e a destra della corrente
            min_page = max(1, st.session_state["current_page"] - half_range)
            max_page = min(total_pages, st.session_state["current_page"] + half_range)

            if max_page - min_page < 6:
                if min_page == 1:
                    max_page = min(7, total_pages)
                elif max_page == total_pages:
                    min_page = max(1, total_pages - 6)

            with pagination_cols[0]:
                if st.button("⏮️", disabled=st.session_state["current_page"] == 1):
                    st.session_state["current_page"] = 1
                    st.rerun()

            with pagination_cols[1]:
                if st.button("◀️", disabled=st.session_state["current_page"] == 1):
                    st.session_state["current_page"] -= 1
                    st.rerun()

            for idx, page_num in enumerate(range(min_page, max_page + 1)):
                with pagination_cols[2 + idx]:  # Inizia dalla terza colonna
                    if st.button(
                        f"{page_num}",
                        key=f"page_{page_num}",
                        use_container_width=True,
                        disabled=(page_num == st.session_state["current_page"]),
                    ):
                        st.session_state["current_page"] = page_num
                        st.rerun()

            with pagination_cols[9]:  # Penultima colonna
                if st.button("▶️", disabled=st.session_state["current_page"] == total_pages):
                    st.session_state["current_page"] += 1
                    st.rerun()

            with pagination_cols[10]:  # Ultima colonna
                if st.button("⏭️", disabled=st.session_state["current_page"] == total_pages):
                    st.session_state["current_page"] = total_pages
                    st.rerun()
                    
    else:
        st.warning("No movies found based on selected filters.")

    if st.button("Back"):
        st.session_state["page"] = "research"
        st.rerun()
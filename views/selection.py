import streamlit as st
from src.movies_utils import get_random_movies, load_preprocessed_data
from src.auth import update_preferences

def show_selection_page():
    st.header("Select Initial Movies (Pick 3-8 Movies)")

    # Carica il dataset e genera 30 film casuali
    movies = load_preprocessed_data("data/preprocessed_filmtv_movies.csv")

    if not st.session_state["movies_to_display"]:
        st.session_state["movies_to_display"] = get_random_movies(movies, num_movies=30)

    col1, col2 = st.columns([1, 1])

    # Variabile per il messaggio di avviso o successo
    alert_message = None
    alert_type = None

    with col1:
        if st.button("Reload Movies"):
            st.session_state["movies_to_display"] = get_random_movies(movies, num_movies=30)
            st.session_state["selected_movies"] = []  # Resetta i film selezionati

    with col2:
        if st.button("Confirm Selection"):
            if not (3 <= len(st.session_state["selected_movies"]) <= 8):
                alert_message = "Please select between 3 to 8 movies before proceeding."
                alert_type = "warning"
            else:
                # Recupera solo gli ID dei film selezionati
                selected_movie_ids = [
                    movie['filmtv_id'] for movie in st.session_state["movies_to_display"]
                    if movie['title'] in st.session_state["selected_movies"]
                ]
                update_preferences(st.session_state["username"], selected_movie_ids)
                alert_message = "Selection saved!"
                alert_type = "success"
                st.session_state["page"] = "filters"

    # Mostra il messaggio di avviso o successo sopra l'elenco dei film
    if alert_message:
        if alert_type == "warning":
            st.warning(alert_message)
        elif alert_type == "success":
            st.success(alert_message)

    # Mostra i film con titolo, durata e anno
    for movie in st.session_state["movies_to_display"]:
        title = movie['title']
        year = movie['year']
        duration = movie['duration']
        label = f"**{title}** (Duration: {duration} min, Year: {year})"
        if st.checkbox(label, key=f"select_{title}"):
            if title not in st.session_state["selected_movies"]:
                st.session_state["selected_movies"].append(title)
        else:
            if title in st.session_state["selected_movies"]:
                st.session_state["selected_movies"].remove(title)
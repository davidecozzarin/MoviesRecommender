import pandas as pd
import streamlit as st
from src.auth import register_user, authenticate_user, get_user, update_preferences, get_preferences, update_disliked ,get_disliked
from src.knn_model import get_recommendations
from src.filtering_functions import filter_movies
import requests
import math

# Configurazione della pagina
st.set_page_config(
    page_title="Film Recommender",
    page_icon="🎥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def load_preprocessed_data(file_path):
    try:
        movies = pd.read_csv(file_path)
        return movies
    except Exception as e:
        st.error(f"Errore durante il caricamento dei dati: {e}")
        return pd.DataFrame()

def get_random_movies(movies_df, num_movies=30, min_avg_vote=7.5):  
    filtered_movies = movies_df[movies_df['avg_vote'] >= min_avg_vote]
    if len(filtered_movies) < num_movies:
        st.warning("Non ci sono abbastanza film con un punteggio medio sufficiente. Mostrando tutti i film disponibili.")
        num_movies = len(filtered_movies)
    return filtered_movies.sample(n=num_movies).to_dict(orient="records")

# Inizializza lo stato della sessione
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["selected_movies"] = []  # Per memorizzare i film selezionati
    st.session_state["recommendations"] = []  # Raccomandazioni finali
    st.session_state["page"] = "login"  # Stato iniziale della navigazione
    st.session_state["movie_details"] = None  # Dettagli del film selezionato

# Funzione per la gestione di login e registrazione
def show_login_register_page():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.header("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login"):
                authenticated, user = authenticate_user(username, password)
                if authenticated:
                    st.success("Login successful!")
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    preferences = get_preferences(username)
                    if preferences:
                        st.session_state["page"] = "filters"
                        st.rerun()
                    else:
                        st.session_state["page"] = "selection"
                        st.rerun()
                else:
                    st.error("Invalid username or password.")

        with tab2:
            st.header("Register")
            new_username = st.text_input("New Username", key="register_username")
            new_password = st.text_input("Password", type="password", key="register_password")

            if st.button("Register"):
                if new_username and new_password:
                    response = register_user(new_username, new_password)
                    if response == "User registered successfully.":
                        st.success(response)
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = new_username
                        st.session_state["page"] = "selection"
                        st.rerun()
                    else:
                        st.error(response)
                        st.rerun()
                else:
                    st.warning("Please provide both username and password.")

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    # st.session_state["selected_movies"] = []
    # st.session_state["recommendations"] = []
    # st.session_state["page"] = "login"
    # st.session_state["movie_details"] = None
    show_login_register_page()
    st.rerun()


def get_movie_poster(title, year):
    """Recupera il poster di un film utilizzando l'API OMDb."""
    api_key = "f34d45dd"  # Sostituisci con la tua chiave API OMDb
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={title}&y={year}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("Response") == "True":
            return data.get("Poster")  # Restituisce l'URL del poster
        else:
            return None  # Nessun poster trovato
    except Exception as e:
        print(f"Errore durante il recupero del poster: {e}")
        return None


# Forza la pagina di login se non autenticato
if not st.session_state["authenticated"]:
    st.session_state["page"] = "login"

st.title("Film Recommender System")

if "movies_to_display" not in st.session_state:
    st.session_state["movies_to_display"] = []

if st.session_state["page"] == "selection":
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

elif st.session_state["page"] == "filters":
     # Barra laterale per il logout e l'accesso alla pagina preferenze
    with st.sidebar:
        st.header("Menu")
        if st.button("Logout"):
            logout()
        if st.button("Preferences"):
            st.session_state["page"] = "preferences"
        if st.button("Research section"):
            st.session_state["page"] = "research"
    
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
    if st.button("Get Recommendations"):
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
        else:
            st.warning("No recommendations found based on your preferences and filters.")

elif st.session_state["page"] == "preferences":
    # Barra laterale per il logout e tornare ai filtri
    with st.sidebar:
        st.header("Menu")
        if st.button("Logout"):
            logout()
        if st.button("Recommandations section"):
            st.session_state["page"] = "filters"
        if st.button("Research section"):
            st.session_state["page"] = "research"

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

elif st.session_state["page"] == "details":
    # Pagina dei dettagli del film
    movie_details = st.session_state.get("movie_details", {})
    if not movie_details:
        st.warning("No movie selected.")
        if st.button("Back"):
            st.session_state["page"] = "preferences"
            st.rerun()
    else:
        st.header(f"Details of '{movie_details['title']}'")

        # Recupera il poster del film
        poster_url = get_movie_poster(movie_details['title'], movie_details.get('year'))
        
        if poster_url:
            st.image(poster_url, caption=f"{movie_details['title']}", use_container_width="always")
        else:
            st.write("Poster not available.")

        st.write(f"**Year**: {movie_details['year']}")
        st.write(f"**Genre**: {movie_details['genre']}")
        st.write(f"**Duration**: {movie_details['duration']} minutes")
        st.write(f"**Country**: {movie_details['country']}")
        st.write(f"**Directors**: {movie_details['directors']}")
        st.write(f"**Actors**: {movie_details['actors']}")
        st.write(f"**Average Vote**: {movie_details['avg_vote']} (from {movie_details['total_votes']} votes)")
        st.write(f"**Description**: {movie_details['description']}")
        st.write(f"**Attributes**: Humor: {movie_details['humor']}, Rhythm: {movie_details['rhythm']}, "
                 f"Effort: {movie_details['effort']}, Tension: {movie_details['tension']}, Erotism: {movie_details['erotism']}")

        if st.button("Back"):
            st.session_state["page"] = "preferences"
            st.rerun()

elif st.session_state["page"] == "results":
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

elif st.session_state["page"] == "result_details":
    # Pagina dei dettagli del film
    movie_details = st.session_state.get("movie_details", {})
    if not movie_details:
        st.warning("No movie selected.")
        if st.button("Back"):
            st.session_state["page"] = "results"
            st.rerun()
    else:
        st.header(f"Details of '{movie_details['title']}'")

        # Recupera il poster del film
        poster_url = get_movie_poster(movie_details['title'], movie_details.get('year'))
        
        if poster_url:
            st.image(poster_url, caption=f"{movie_details['title']}", use_container_width="always")
        else:
            st.write("Poster not available.")

        st.write(f"**Year**: {movie_details['year']}")
        st.write(f"**Genre**: {movie_details['genre']}")
        st.write(f"**Duration**: {movie_details['duration']} minutes")
        st.write(f"**Country**: {movie_details['country']}")
        st.write(f"**Directors**: {movie_details['directors']}")
        st.write(f"**Actors**: {movie_details['actors']}")
        st.write(f"**Average Vote**: {movie_details['avg_vote']} (from {movie_details['total_votes']} votes)")
        st.write(f"**Description**: {movie_details['description']}")
        st.write(f"**Attributes**: Humor: {movie_details['humor']}, Rhythm: {movie_details['rhythm']}, "
                 f"Effort: {movie_details['effort']}, Tension: {movie_details['tension']}, Erotism: {movie_details['erotism']}")

        if st.button("Back"):
            st.session_state["page"] = "research_results"
            st.rerun()

elif st.session_state["page"] == "research":
     # Barra laterale per il logout e l'accesso alla pagina preferenze
    with st.sidebar:
        st.header("Menu")
        if st.button("Logout"):
            logout()
        if st.button("Preferences"):
            st.session_state["page"] = "preferences"
        if st.button("Reccomandation section"):
            st.session_state["page"] = "filters"
    
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


elif st.session_state["page"] == "research_results":
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
        if st.session_state.get("from_page") == "research_results":
            st.session_state["page"] = "research"
            st.rerun()

# Sezione di login e registrazione

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    show_login_register_page()

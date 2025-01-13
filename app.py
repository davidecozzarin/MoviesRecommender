import pandas as pd
import streamlit as st
from src.auth import register_user, authenticate_user, get_user, update_preferences, get_preferences, update_disliked ,get_disliked
from src.knn_model import get_recommendations
import requests

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


def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["selected_movies"] = []
    st.session_state["recommendations"] = []
    st.session_state["page"] = "login"
    st.session_state["movie_details"] = None  # Dettagli del film selezionato


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

    with col1:
        if st.button("Reload Movies"):
            st.session_state["movies_to_display"] = get_random_movies(movies, num_movies=30)
            st.session_state["selected_movies"] = []  # Resetta i film selezionati

    with col2:
        if st.button("Confirm Selection"):
            if not (3 <= len(st.session_state["selected_movies"]) <= 8):
                st.warning("Please select between 3 to 8 movies before proceeding.")
            else:
                # Recupera solo gli ID dei film selezionati
                selected_movie_ids = [
                    movie['filmtv_id'] for movie in st.session_state["movies_to_display"]
                    if movie['title'] in st.session_state["selected_movies"]
                ]
                update_preferences(st.session_state["username"], selected_movie_ids)
                st.success("Selection saved!")
                st.session_state["page"] = "filters"

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

        print(f"Filters applied: {filters}")

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
        if st.button("Back to Filters"):
            st.session_state["page"] = "filters"

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
            st.session_state["page"] = "results"
            st.rerun()

# Sezione di login e registrazione
if not st.session_state["authenticated"]:
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
                else:
                    st.session_state["page"] = "selection"
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
                else:
                    st.error(response)
            else:
                st.warning("Please provide both username and password.")

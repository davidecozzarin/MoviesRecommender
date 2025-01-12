import pandas as pd
import streamlit as st
from src.auth import register_user, authenticate_user, get_user, update_preferences, get_preferences
from src.knn_model import get_recommendations

# Configurazione della pagina
st.set_page_config(
    page_title="Film Recommender",
    page_icon="🎥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def load_preprocessed_data(file_path):
    """
    Carica i dati preprocessati dal file CSV.
    """
    try:
        movies = pd.read_csv(file_path)
        return movies
    except Exception as e:
        st.error(f"Errore durante il caricamento dei dati: {e}")
        return pd.DataFrame()

def get_random_movies(movies_df, num_movies=30, min_avg_vote=7.5):  
    """
    Estrae un numero di film casuali con un punteggio medio minimo specificato.
    """
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
    st.session_state["page"] = "home"  # Stato iniziale della navigazione

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["selected_movies"] = []
    st.session_state["recommendations"] = []
    st.session_state["page"] = "home"

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
                update_preferences(st.session_state["username"], st.session_state["selected_movies"])
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
    st.header("Search for Movie Recommendations")

    # Recupera i film selezionati dall'utente
    selected_movies = st.session_state.get("selected_movies", [])
    st.write("Selected Movies:")
    st.write(selected_movies)

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

        recommendations = get_recommendations(selected_movies, [], filters)

        if len(recommendations) > 0:  # Verifica se ci sono risultati
            st.session_state["recommendations"] = recommendations
            st.session_state["page"] = "results"
        else:
            st.warning("No recommendations found based on your preferences and filters.")

elif st.session_state["page"] == "results":
    st.header("Recommended Movies")
    recommendations = st.session_state.get("recommendations", [])

    if len(recommendations) > 0:
        for title in recommendations:
            st.write(title)
    else:
        st.warning("No recommendations found based on your preferences and filters.")

    if st.button("Back"):
        st.session_state["page"] = "filters"

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

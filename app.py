import streamlit as st
from src.auth import register_user, authenticate_user, get_user, update_preferences, get_preferences
from src.data_preprocessing import load_and_preprocess_data
import random

# Configurazione della pagina
st.set_page_config(
    page_title="FilmRecommender",
    page_icon="🎥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Funzione per selezionare 5 film casuali
def get_random_movies(movies_df, num_movies=10):
    return movies_df.sample(n=num_movies).to_dict(orient="records")

# Initialize session state variables for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["selected_movies"] = []  # Per memorizzare i film selezionati
    st.session_state["remaining_picks"] = 5  # Per contare i film rimanenti

# Function to reset authentication state (logout)
def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["selected_movies"] = []
    st.session_state["remaining_picks"] = 5

# Main page
st.title("Film Recommender System")

# If user is authenticated, show personalized content
if st.session_state["authenticated"]:
    st.sidebar.success(f"Logged in as {st.session_state['username']}")

    # Add a logout button in the sidebar
    if st.sidebar.button("Logout"):
        logout()

    # Fetch user info from the database
    user_info = get_user(st.session_state["username"])
    preferences = get_preferences(st.session_state["username"])

    # Se l'utente non ha selezionato preferenze, avvia la selezione
    if not preferences:
        st.header("Select Your Top 5 Movies")

        # Carica il dataset dei film
        movies = load_and_preprocess_data("data/filmtv_movies.csv")

        # Inizializza lo stato per i film disponibili
        if "current_pool" not in st.session_state or st.session_state["remaining_picks"] == 5:
            st.session_state["current_pool"] = get_random_movies(movies, num_movies=10)
            st.session_state["last_selected"] = None

        # Mostra i 10 film correnti come opzioni selezionabili
        selected_movie = st.radio(
            "Pick a movie you like:",
            options=[movie["title"] for movie in st.session_state["current_pool"]],
            key=f"pick_{5 - st.session_state['remaining_picks']}"  # Un key unico per ogni selezione
        )

        # Conferma la selezione e aggiorna lo stato
        if st.button("Confirm Selection"):
            if selected_movie:
                # Salva il film selezionato e aggiorna la lista
                st.session_state["selected_movies"].append(selected_movie)
                st.session_state["remaining_picks"] -= 1
                st.session_state["current_pool"] = get_random_movies(movies, num_movies=10)
                st.session_state["last_selected"] = selected_movie

        # Una volta completate le selezioni
        if st.session_state["remaining_picks"] == 0:
            st.success("You have selected your top 5 movies!")
            st.write("Here are your selections:")
            st.write(st.session_state["selected_movies"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Preferences"):
                    update_preferences(st.session_state["username"], st.session_state["selected_movies"])
                    st.success("Preferences saved successfully!")
                    st.session_state["selected_movies"] = []  # Resetta le selezioni
                    st.session_state["remaining_picks"] = 5  # Resetta il contatore
            with col2:
                if st.button("Restart Selection"):
                    st.session_state["selected_movies"] = []
                    st.session_state["remaining_picks"] = 5  # Resetta il contatore
                    st.session_state["current_pool"] = get_random_movies(movies, num_movies=10)  # Reset pool

    else:
        st.header(f"Welcome, {st.session_state['username']}!")
        st.write("Enjoy personalized movie recommendations.")
        st.write("Your preferences:")
        st.write(preferences)

# If not authenticated, show login and registration tabs
else:
    tab1, tab2 = st.tabs(["Login", "Register"])

    # Login Tab
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
            else:
                st.error("Invalid username or password.")

    # Registration Tab
    with tab2:
        st.header("Register")
        new_username = st.text_input("New Username", key="register_username")
        new_password = st.text_input("New Password", type="password", key="register_password")
        profile_pic = st.file_uploader("Upload Profile Picture (Optional)", type=["png", "jpg", "jpeg"])

        if st.button("Register"):
            if new_username and new_password:
                profile_pic_data = profile_pic.read() if profile_pic else None
                response = register_user(new_username, new_password, profile_pic_data)
                if response == "User registered successfully.":
                    st.success(response)
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = new_username
                else:
                    st.error(response)
            else:
                st.warning("Please provide both username and password.")

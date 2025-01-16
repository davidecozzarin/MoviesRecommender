import pandas as pd
import streamlit as st
from views.login_register import show_login_register_page
from views.selection import show_selection_page
from views.filters import show_filters_page
from views.preferences import show_preferences_page
from views.details import show_details_page, show_results_details_page
from views.results import show_results_page
from views.research import show_research_page, show_research_results_page

# Configurazione della pagina
st.set_page_config(
    page_title="MyCinema",
    page_icon="🎥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inizializza lo stato della sessione
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["selected_movies"] = []  # Per memorizzare i film selezionati
    st.session_state["recommendations"] = []  # Raccomandazioni finali
    st.session_state["page"] = "login"  # Stato iniziale della navigazione
    st.session_state["movie_details"] = None  # Dettagli del film selezionato

# Funzione per la gestione di login e registrazione


def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["selected_movies"] = []
    st.session_state["recommendations"] = []
    st.session_state["page"] = "login"
    st.session_state["movie_details"] = None
    show_login_register_page()
    st.rerun()


# Forza la pagina di login se non autenticato
if not st.session_state["authenticated"]:
    st.session_state["page"] = "login"
st.title("MyCinema")

if "movies_to_display" not in st.session_state:
    st.session_state["movies_to_display"] = []

if st.session_state["page"] == "selection":
    show_selection_page()

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
    show_filters_page()

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
    show_preferences_page()

elif st.session_state["page"] == "details":
    # Pagina dei dettagli del film
    show_details_page()
        

elif st.session_state["page"] == "results":
    show_results_page()

elif st.session_state["page"] == "result_details":
    # Pagina dei dettagli del film
    show_results_details_page()

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
    show_research_page()


elif st.session_state["page"] == "research_results":
    show_research_results_page()

# Sezione di login e registrazione

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    show_login_register_page()

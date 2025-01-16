import streamlit as st
from src.auth import authenticate_user, get_preferences, register_user

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

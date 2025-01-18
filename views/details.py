import streamlit as st
from src.movies_utils import get_movie_poster

def show_details_page():
    movie_details = st.session_state.get("movie_details", {})
    if not movie_details:
        st.warning("No movie selected.")

    else:
        st.header(f"Details of '{movie_details['title']}'")

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

    
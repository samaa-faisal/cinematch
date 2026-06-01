import streamlit as st
from recommender import recommend, get_movie_titles

st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #2b1055 0%, #12091f 45%, #050505 100%);
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    text-align: center;
    padding: 35px 20px 25px 20px;
}

.hero-title {
    font-size: 72px;
    font-weight: 900;
    color: white;
    letter-spacing: -2px;
}

.hero-subtitle {
    font-size: 22px;
    color: #d8d8d8;
    margin-top: 10px;
}

.stButton button {
    background: linear-gradient(90deg, #e50914, #ff3b3b);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 12px 32px;
    font-weight: 800;
    font-size: 16px;
}

.stButton button:hover {
    background: linear-gradient(90deg, #ff3b3b, #e50914);
    color: white;
    transform: scale(1.02);
}

.section-title {
    font-size: 34px;
    font-weight: 800;
    margin-top: 35px;
    margin-bottom: 20px;
    color: white;
}

.movie-card {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 20px;
    backdrop-filter: blur(8px);
    transition: transform 0.3s ease;
}

.movie-card:hover {
    transform: scale(1.03);
}

.movie-title {
    font-size: 19px;
    font-weight: 800;
    color: white;
    margin-top: 12px;
    min-height: 50px;
}

.movie-meta {
    font-size: 14px;
    color: #f5c542;
    font-weight: 700;
    margin-bottom: 8px;
}

.movie-genre {
    font-size: 13px;
    color: #bdbdbd;
    margin-bottom: 10px;
}

.movie-overview {
    font-size: 13px;
    color: #eeeeee;
    line-height: 1.5;
}

.footer {
    text-align: center;
    color: #9c9c9c;
    margin-top: 55px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-title">🎬 CineMatch</div>
    <div class="hero-subtitle">Discover movies that match your taste instantly.</div>
</div>
""", unsafe_allow_html=True)

movie_list = get_movie_titles()

selected_movie = st.selectbox(
    "Search or choose a movie:",
    movie_list
)

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "show_more" not in st.session_state:
    st.session_state.show_more = False

if st.button("Find Similar Movies"):
    with st.spinner("Finding the best matches for you..."):
        st.session_state.recommendations = recommend(selected_movie, total_results=20)
        st.session_state.show_more = False

if st.session_state.recommendations:
    st.markdown("<div class='section-title'>Recommended for you</div>", unsafe_allow_html=True)

    display_count = 20 if st.session_state.show_more else 10
    visible_movies = st.session_state.recommendations[:display_count]

    for row in range(0, len(visible_movies), 5):
        cols = st.columns(5)

        for col_index, movie in enumerate(visible_movies[row:row + 5]):
            with cols[col_index]:
                st.image(movie["poster"], use_container_width=True)
                
                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div class="movie-title">{movie["title"]}</div>
                    <div class="movie-meta">⭐ {movie["rating"]} | {movie["release_date"]}</div>
                    <div class="movie-genre">{movie["genres"]}</div>
                    <div class="movie-overview">{movie["overview"][:180]}...</div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.show_more:
        if st.button("Show More Recommendations"):
            st.session_state.show_more = True
            st.rerun()

st.markdown("<div class='footer'>Powered by TMDB API</div>", unsafe_allow_html=True)

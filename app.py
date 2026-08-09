import streamlit as st
from recommender import (
    get_content_recommendations,
    get_collaborative_recommendations,
    get_movie_details as _get_movie_details,
    movies,
    ratings,
)


@st.cache_data(show_spinner=False, ttl=3600)
def get_movie_details(title):
    """Cached wrapper so each movie's TMDB lookup only happens once, not on every click."""
    return _get_movie_details(title)


# ---------- Page config ----------
st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

# ---------- Netflix-style CSS ----------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@300;400;600;700&display=swap');

    .stApp {
        background-color: #141414;
        color: #ffffff;
    }

    h1.cine-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 4rem;
        color: #E50914;
        letter-spacing: 3px;
        margin-bottom: 0;
    }

    p.cine-subtitle {
        font-family: 'Poppins', sans-serif;
        color: #b3b3b3;
        font-size: 1rem;
        margin-top: 0;
        margin-bottom: 2rem;
    }

    div[data-baseweb="select"] > div {
        background-color: #2b2b2b;
        border-color: #404040;
        color: white;
        font-family: 'Poppins', sans-serif;
    }

    .stButton>button {
        background-color: #E50914;
        color: white;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        border: none;
        border-radius: 4px;
        padding: 0.6rem 2rem;
        transition: background-color 0.2s ease;
    }

    .stButton>button:hover {
        background-color: #f6121d;
        color: white;
    }

    .movie-card {
        background-color: #1c1c1c;
        border-radius: 6px;
        overflow: hidden;
        transition: transform 0.25s ease;
        margin-bottom: 1.5rem;
        height: 100%;
    }

    .movie-card:hover {
        transform: scale(1.04);
        box-shadow: 0 8px 20px rgba(0,0,0,0.6);
    }

    .movie-poster {
        width: 100%;
        aspect-ratio: 2/3;
        object-fit: cover;
        background-color: #333;
    }

    .movie-info {
        padding: 0.8rem;
        font-family: 'Poppins', sans-serif;
    }

    .movie-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.3rem;
        line-height: 1.3;
    }

    .movie-rating {
        color: #f5c518;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }

    .movie-overview {
        color: #b3b3b3;
        font-size: 0.78rem;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .movie-link {
        display: inline-block;
        margin-top: 0.6rem;
        color: #E50914;
        font-family: 'Poppins', sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        text-decoration: none;
    }

    .movie-link:hover {
        text-decoration: underline;
    }

    .movie-link-disabled {
        display: inline-block;
        margin-top: 0.6rem;
        color: #666;
        font-family: 'Poppins', sans-serif;
        font-size: 0.78rem;
    }

    label, .stSelectbox label, .stNumberInput label {
        font-family: 'Poppins', sans-serif !important;
        color: #e5e5e5 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<h1 class="cine-title">CINEMATCH</h1>', unsafe_allow_html=True)
st.markdown('<p class="cine-subtitle">Your personal movie recommendation engine</p>', unsafe_allow_html=True)

# ---------- Controls ----------
col1, col2 = st.columns([1, 2])

with col1:
    option = st.selectbox("Recommendation type", ["Content-Based", "Collaborative Filtering"])

with col2:
    if option == "Content-Based":
        selected_movie = st.selectbox("Pick a movie you like", movies['title'].values)
    else:
        selected_user = st.number_input(
            "Enter User ID",
            min_value=1,
            max_value=int(ratings.userId.max()),
            step=1
        )

recommend_clicked = st.button("▶  Recommend")

# ---------- Poster grid renderer ----------
def render_movie_grid(titles):
    cols_per_row = 5
    for i in range(0, len(titles), cols_per_row):
        row_titles = titles[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, movie_title in zip(cols, row_titles):
            details = get_movie_details(movie_title)
            poster = details["poster"] or "https://via.placeholder.com/300x450/1c1c1c/808080?text=No+Poster"
            overview = details["overview"]
            rating = details["rating"]
            tmdb_url = details.get("url")
            rating_display = f"⭐ {rating:.1f}" if isinstance(rating, (int, float)) else "⭐ N/A"

            link_html = (
                f'<a href="{tmdb_url}" target="_blank" class="movie-link">View on TMDB →</a>'
                if tmdb_url else
                '<span class="movie-link-disabled">No link available</span>'
            )

            with col:
                st.markdown(f"""
                    <div class="movie-card">
                        <img class="movie-poster" src="{poster}" />
                        <div class="movie-info">
                            <div class="movie-title">{movie_title}</div>
                            <div class="movie-rating">{rating_display}</div>
                            <div class="movie-overview">{overview}</div>
                            {link_html}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# ---------- Results ----------
if recommend_clicked:
    st.markdown("---")
    with st.spinner("Finding recommendations..."):
        if option == "Content-Based":
            st.markdown(f"### Because you liked *{selected_movie}*")
            results = get_content_recommendations(selected_movie)
        else:
            st.markdown(f"### Recommended for User {selected_user}")
            results = get_collaborative_recommendations(selected_user)

    render_movie_grid(results)
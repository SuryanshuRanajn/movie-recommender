import os
import requests
import pandas as pd
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

# ---------- Load environment variables ----------
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# On Streamlit Cloud, secrets aren't always exposed via os.getenv().
# Fall back to st.secrets if the key wasn't found locally.
if not TMDB_API_KEY:
    try:
        import streamlit as st
        TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
    except Exception:
        TMDB_API_KEY = None

# ---------- Load data ----------
movies = pd.read_csv('data/movies.csv')
ratings = pd.read_csv('data/ratings.csv')

# ---------- Content-Based Filtering ----------
movies['genres'] = movies['genres'].str.replace('|', ' ', regex=False)
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['genres'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()


def get_content_recommendations(title, n=10):
    """Recommend movies similar to the given title based on genre similarity."""
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n + 1]  # skip the movie itself
    movie_indices = [i[0] for i in sim_scores]
    return movies['title'].iloc[movie_indices].tolist()


# ---------- Collaborative Filtering ----------
user_movie_matrix = ratings.pivot_table(index='userId', columns='movieId', values='rating').fillna(0)
svd = TruncatedSVD(n_components=20, random_state=42)
matrix_reduced = svd.fit_transform(user_movie_matrix)
reconstructed_matrix = svd.inverse_transform(matrix_reduced)
predicted_ratings = pd.DataFrame(
    reconstructed_matrix,
    columns=user_movie_matrix.columns,
    index=user_movie_matrix.index
)


def get_collaborative_recommendations(user_id, n=10):
    """Recommend movies for a user based on latent factors learned via SVD."""
    user_ratings = predicted_ratings.loc[user_id]
    already_rated = ratings[ratings.userId == user_id]['movieId']
    recommendations = user_ratings.drop(already_rated, errors='ignore').sort_values(ascending=False).head(n)
    return movies[movies.movieId.isin(recommendations.index)]['title'].tolist()


# ---------- TMDB Poster + Description Fetching ----------
def get_movie_details(title):
    """Fetch poster URL, overview, rating, and TMDB page link for a movie title.
    Matches by release year (extracted from the MovieLens title) to avoid picking
    the wrong movie when a franchise has multiple entries (e.g. Toy Story 1-5)."""
    if not TMDB_API_KEY:
        return {"poster": None, "overview": "No description available.", "rating": "N/A", "url": None}

    # "Toy Story (1995)" -> clean_title="Toy Story", year="1995"
    if ' (' in title and title.endswith(')'):
        clean_title = title.rsplit(' (', 1)[0]
        year = title.rsplit(' (', 1)[1].rstrip(')')
    else:
        clean_title = title
        year = None

    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": clean_title}
    if year and year.isdigit():
        params["year"] = year

    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        results = data.get("results")

        if not results and year:
            # Retry without the year filter in case it was too strict
            params.pop("year", None)
            response = requests.get(url, params=params, timeout=15)
            results = response.json().get("results")

        if results:
            # Prefer a result whose release year matches exactly
            result = results[0]
            if year:
                for r in results:
                    if r.get("release_date", "").startswith(year):
                        result = r
                        break

            poster_path = result.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            overview = result.get("overview") or "No description available."
            rating = result.get("vote_average", "N/A")
            movie_id = result.get("id")
            tmdb_url = f"https://www.themoviedb.org/movie/{movie_id}" if movie_id else None
            return {"poster": poster_url, "overview": overview, "rating": rating, "url": tmdb_url}
    except Exception as e:
        print(f"Error fetching details for {title}: {e}")

    return {"poster": None, "overview": "No description available.", "rating": "N/A", "url": None}
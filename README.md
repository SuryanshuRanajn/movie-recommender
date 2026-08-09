# 🎬 CineMatch — Movie Recommendation System

A movie recommendation web app built with two different recommendation approaches, wrapped in a Netflix-inspired UI with live poster and metadata fetching from TMDB.

**🔗 Live Demo:** [cinematch-monster-movie.streamlit.app](https://cinematch-monster-movie.streamlit.app/)

---

## Features

- **Content-Based Filtering** — recommends movies similar to one you like, using TF-IDF vectorization on genres and cosine similarity
- **Collaborative Filtering** — recommends movies based on user rating patterns, using SVD (matrix factorization) on the user-item ratings matrix
- **Live movie data** — posters, ratings, and descriptions fetched from [TMDB](https://www.themoviedb.org/)'s API in real time
- **Netflix-style UI** — dark theme, custom fonts (Bebas Neue + Poppins), poster grid with hover effects
- **Direct links** — each recommendation links out to its TMDB page for trailers, cast info, and more

## Tech Stack

- **Python** — pandas, scikit-learn (TF-IDF, cosine similarity, TruncatedSVD)
- **Streamlit** — UI and deployment
- **TMDB API** — posters, ratings, descriptions
- **Dataset** — [MovieLens (ml-latest-small)](https://grouplens.org/datasets/movielens/latest/)

## How It Works

1. **Content-based recommendations**: Movie genres are vectorized using TF-IDF, and cosine similarity is computed between all movies. Given a movie you like, the app returns the most similar titles based on genre overlap.

2. **Collaborative filtering**: The user-item ratings matrix is decomposed into latent factors using Truncated SVD. This captures hidden patterns in user taste (e.g. "users who like X also tend to like Y") without relying on genre metadata, and predicts ratings for movies a user hasn't seen yet.

3. **Live metadata**: For each recommended title, the app queries the TMDB API (matching by release year to correctly handle franchises with multiple entries) to fetch the poster, description, and rating.

## Running Locally

```bash
git clone https://github.com/SuryanshuRanajn/movie-recommender.git
cd movie-recommender
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root with your own [TMDB API key](https://www.themoviedb.org/settings/api):
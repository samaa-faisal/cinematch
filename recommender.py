import os
import requests
import pandas as pd
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

movies = pd.read_csv("processed_movies.csv")

cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(movies["tags"]).toarray()
similarity = cosine_similarity(vectors)


def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    poster_path = data.get("poster_path")
    poster_url = (
        "https://image.tmdb.org/t/p/w500/" + poster_path
        if poster_path
        else "https://via.placeholder.com/500x750?text=No+Image"
    )

    genres = ", ".join([genre["name"] for genre in data.get("genres", [])])

    return {
        "poster": poster_url,
        "rating": round(data.get("vote_average", 0), 1),
        "release_date": data.get("release_date", "N/A"),
        "overview": data.get("overview", "No description available."),
        "genres": genres if genres else "N/A",
    }


def recommend(movie, total_results=20):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:total_results + 1]

    recommendations = []

    for i in movie_list:
        movie_id = int(movies.iloc[i[0]].movie_id)
        details = fetch_movie_details(movie_id)

        recommendations.append({
            "title": movies.iloc[i[0]].title,
            "poster": details["poster"],
            "rating": details["rating"],
            "release_date": details["release_date"],
            "overview": details["overview"],
            "genres": details["genres"],
        })

    return recommendations


def get_movie_titles():
    return movies["title"].values

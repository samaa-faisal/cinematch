import ast
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")

movies = movies.merge(credits, on="title")
movies = movies[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]]
movies.dropna(inplace=True)


def convert(text):
    return [item["name"] for item in ast.literal_eval(text)]


def get_top_cast(text):
    return [item["name"] for item in ast.literal_eval(text)[:3]]


def get_director(text):
    for item in ast.literal_eval(text):
        if item["job"] == "Director":
            return [item["name"]]
    return []


def remove_space(words):
    return [word.replace(" ", "") for word in words]


movies["genres"] = movies["genres"].apply(convert)
movies["keywords"] = movies["keywords"].apply(convert)
movies["cast"] = movies["cast"].apply(get_top_cast)
movies["crew"] = movies["crew"].apply(get_director)
movies["overview"] = movies["overview"].apply(lambda x: x.split())

movies["genres"] = movies["genres"].apply(remove_space)
movies["keywords"] = movies["keywords"].apply(remove_space)
movies["cast"] = movies["cast"].apply(remove_space)
movies["crew"] = movies["crew"].apply(remove_space)

movies["tags"] = (
    movies["overview"]
    + movies["genres"]
    + movies["keywords"]
    + movies["cast"]
    + movies["crew"]
)

new_movies = movies[["movie_id", "title", "tags"]].copy()
new_movies["tags"] = new_movies["tags"].apply(lambda x: " ".join(x).lower())

cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(new_movies["tags"]).toarray()
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
    movie_index = new_movies[new_movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:total_results + 1]

    recommendations = []

    for i in movie_list:
        movie_id = int(new_movies.iloc[i[0]].movie_id)
        details = fetch_movie_details(movie_id)

        recommendations.append({
            "title": new_movies.iloc[i[0]].title,
            "poster": details["poster"],
            "rating": details["rating"],
            "release_date": details["release_date"],
            "overview": details["overview"],
            "genres": details["genres"],
        })

    return recommendations


def get_movie_titles():
    return new_movies["title"].values
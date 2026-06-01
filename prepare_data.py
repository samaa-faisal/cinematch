import ast
import pandas as pd

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

movies["genres"] = movies["genres"].apply(convert).apply(remove_space)
movies["keywords"] = movies["keywords"].apply(convert).apply(remove_space)
movies["cast"] = movies["cast"].apply(get_top_cast).apply(remove_space)
movies["crew"] = movies["crew"].apply(get_director).apply(remove_space)
movies["overview"] = movies["overview"].apply(lambda x: x.split())

movies["tags"] = (
    movies["overview"] +
    movies["genres"] +
    movies["keywords"] +
    movies["cast"] +
    movies["crew"]
)

final_data = movies[["movie_id", "title", "tags"]].copy()
final_data["tags"] = final_data["tags"].apply(lambda x: " ".join(x).lower())

final_data.to_csv("processed_movies.csv", index=False)

print("processed_movies.csv created successfully!")
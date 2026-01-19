import pandas as pd
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://tbp_user:x2G3nWYf@cluster0.u8yh2mj.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["recommender_db"]

movies_col = db.movies
genres_col = db.genres

movies_col.delete_many({})
genres_col.delete_many({})

df = pd.read_csv("data/netflix_titles.csv")

df = df.sample(n=100, random_state=42)

df = df[
    [
        "show_id",
        "title",
        "type",
        "release_year",
        "listed_in",
        "description",
    ]
]

GENRE_MAP = {
    "Action & Adventure": "Action",
    "Sci-Fi & Fantasy": "Sci-Fi",
    "Dramas": "Drama",
    "Comedies": "Comedy",
    "Thrillers": "Thriller",
    "Romantic Movies": "Romance",
}

genre_ids = {}
for idx, genre in enumerate(set(GENRE_MAP.values()), start=1):
    gid = f"g{idx}"
    genre_ids[genre] = gid
    genres_col.insert_one(
        {
            "_id": gid,
            "name": genre,
        }
    )

print("✔ Ubaceni žanrovi:", genre_ids)

def extract_genres(listed_in_value):
    genres = []
    if pd.isna(listed_in_value):
        return genres

    for raw, clean in GENRE_MAP.items():
        if raw in listed_in_value:
            genres.append(genre_ids[clean])
    return genres

inserted_movies = 0

for _, row in df.iterrows():
    genre_ids_for_movie = extract_genres(row["listed_in"])

    if not genre_ids_for_movie:
        continue

    movie = {
        "_id": row["show_id"],
        "title": row["title"],
        "type": row["type"],
        "releaseYear": int(row["release_year"]),
        "description": row["description"],
        "genreIds": genre_ids_for_movie,
        "averageRating": round(3.5 + (hash(row["title"]) % 15) / 10, 1),
        "views": 0,
    }

    movies_col.insert_one(movie)
    inserted_movies += 1

print("Ubaceni filmovi:", inserted_movies)

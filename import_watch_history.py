from pymongo import MongoClient
from datetime import datetime, timedelta
import random

MONGO_URI = "mongodb+srv://tbp_user:x2G3nWYf@cluster0.u8yh2mj.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["recommender_db"]

watch_col = db.watch_history
movies_col = db.movies
users_col = db.users

watch_col.delete_many({})

users = list(users_col.find({}, {"_id": 1}))
movies = list(movies_col.find({}, {"_id": 1}))

USER_PREFERENCES = {
    "u1": ["Action", "Sci-Fi"],
    "u2": ["Drama", "Romance"],
    "u3": ["Action", "Thriller"]
}

genre_map = {
    g["_id"]: g["name"] for g in db.genres.find({})
}

watch_entries = []

for user in users:
    uid = user["_id"]
    preferred = USER_PREFERENCES.get(uid, [])

    for _ in range(random.randint(5, 10)):
        movie = random.choice(movies)
        movie_doc = movies_col.find_one({"_id": movie["_id"]})

        movie_genres = [genre_map[g] for g in movie_doc["genreIds"]]

        # gledaj samo ako se poklapa barem jedan žanr
        if not set(movie_genres).intersection(preferred):
            continue

        watch_entries.append(
            {
                "userId": uid,
                "movieId": movie["_id"],
                "watchedAt": datetime.utcnow() - timedelta(days=random.randint(1, 30))
            }
        )

if watch_entries:
    watch_col.insert_many(watch_entries)

print("Ubaceni zapisi u watch_history:", len(watch_entries))

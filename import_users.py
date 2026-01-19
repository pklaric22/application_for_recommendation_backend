from pymongo import MongoClient

MONGO_URI = "mongodb+srv://tbp_user:x2G3nWYf@cluster0.u8yh2mj.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["recommender_db"]

users_col = db.users

users_col.delete_many({})

users = [
    {
        "_id": "u1",
        "name": "Patrik",
        "country": "Croatia"
    },
    {
        "_id": "u2",
        "name": "Ana",
        "country": "Germany"
    },
    {
        "_id": "u3",
        "name": "Marko",
        "country": "Croatia"
    }
]

users_col.insert_many(users)

print("Ubaceni useri:", len(users))

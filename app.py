from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient(
    "mongodb+srv://tbp_user:x2G3nWYf@cluster0.u8yh2mj.mongodb.net/?appName=Cluster0"
)
db = client["recommender_db"]


@app.route("/") 
def home():
    return jsonify({"message": "Backend radi"})


@app.route("/users", methods=["GET"])
def get_users():
    users = list(
        db.users.find({}, {"_id": 1, "name": 1, "country": 1})
    )
    return jsonify(users)


@app.route("/test-db")
def test_db():
    try:
        return jsonify({
            "status": "MongoDB connection OK",
            "collections": db.list_collection_names()
        })
    except Exception as e:
        return jsonify({
            "status": "MongoDB connection FAILED",
            "error": str(e)
        }), 500


@app.route("/movies/full", methods=["GET"])
def get_movies_with_genres():
    pipeline = [
        {
            "$lookup": {
                "from": "genres",
                "localField": "genreIds",
                "foreignField": "_id",
                "as": "genres"
            }
        },
        {
            "$project": {
                "_id": 1,
                "title": 1,
                "type": 1,
                "releaseYear": 1,
                "description": 1,
                "averageRating": 1,
                "views": 1,
                "genres.name": 1
            }
        }
    ]
    return jsonify(list(db.movies.aggregate(pipeline)))


@app.route("/movies/genre/<genre_name>", methods=["GET"])
def get_movies_by_genre(genre_name):
    genre = db.genres.find_one({"name": genre_name}, {"_id": 1})
    if not genre:
        return jsonify([])

    pipeline = [
        {"$match": {"genreIds": genre["_id"]}},
        {
            "$lookup": {
                "from": "genres",
                "localField": "genreIds",
                "foreignField": "_id",
                "as": "genres"
            }
        },
        {
            "$project": {
                "_id": 1,
                "title": 1,
                "type": 1,
                "releaseYear": 1,
                "averageRating": {"$ifNull": ["$averageRating", 0]},
                "genres": {
                    "$map": {
                        "input": "$genres",
                        "as": "g",
                        "in": {"name": "$$g.name"}
                    }
                }
            }
        }
    ]

    return jsonify(list(db.movies.aggregate(pipeline)))


@app.route("/movies/popular", methods=["GET"])
def get_popular_movies():
    pipeline = [
        {"$group": {"_id": "$movieId", "views": {"$sum": 1}}},
        {"$sort": {"views": -1}},
        {"$limit": 5},
        {
            "$lookup": {
                "from": "movies",
                "localField": "_id",
                "foreignField": "_id",
                "as": "movie"
            }
        },
        {"$unwind": "$movie"},
        {
            "$project": {
                "_id": 0,
                "movieId": "$_id",
                "title": "$movie.title",
                "views": 1
            }
        }
    ]
    return jsonify(list(db.watch_history.aggregate(pipeline)))


@app.route("/movies/popular/country/<country>", methods=["GET"])
def get_popular_movies_by_country(country):
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "userId",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {"$match": {"user.country": country}},
        {"$group": {"_id": "$movieId", "views": {"$sum": 1}}},
        {"$sort": {"views": -1}},
        {"$limit": 5},
        {
            "$lookup": {
                "from": "movies",
                "localField": "_id",
                "foreignField": "_id",
                "as": "movie"
            }
        },
        {"$unwind": "$movie"},
        {
            "$project": {
                "_id": 0,
                "country": country,
                "movieId": "$_id",
                "title": "$movie.title",
                "views": 1
            }
        }
    ]
    return jsonify(list(db.watch_history.aggregate(pipeline)))


@app.route("/recommendations/<user_id>", methods=["GET"])
def recommend_for_user(user_id):
    pipeline = [
        {"$match": {"userId": user_id}},
        {
            "$lookup": {
                "from": "movies",
                "localField": "movieId",
                "foreignField": "_id",
                "as": "watchedMovie"
            }
        },
        {"$unwind": "$watchedMovie"},
        {
            "$project": {
                "watchedMovieId": "$watchedMovie._id",
                "genreIds": "$watchedMovie.genreIds"
            }
        },
        {"$unwind": "$genreIds"},
        {
            "$lookup": {
                "from": "movies",
                "localField": "genreIds",
                "foreignField": "genreIds",
                "as": "candidateMovie"
            }
        },
        {"$unwind": "$candidateMovie"},
        {
            "$match": {
                "$expr": {
                    "$ne": ["$candidateMovie._id", "$watchedMovieId"]
                }
            }
        },
        {
            "$lookup": {
                "from": "genres",
                "localField": "candidateMovie.genreIds",
                "foreignField": "_id",
                "as": "genres"
            }
        },
        {
            "$project": {
                "_id": "$candidateMovie._id",
                "title": "$candidateMovie.title",
                "type": "$candidateMovie.type",
                "releaseYear": "$candidateMovie.releaseYear",
                "averageRating": {
                    "$ifNull": ["$candidateMovie.averageRating", 0]
                },
                "genres": {
                    "$map": {
                        "input": "$genres",
                        "as": "g",
                        "in": {"name": "$$g.name"}
                    }
                }
            }
        },
        {"$group": {"_id": "$title", "movie": {"$first": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": "$movie"}},
        {"$limit": 5}
    ]

    return jsonify({
        "userId": user_id,
        "recommendations": list(db.watch_history.aggregate(pipeline))
    })


@app.route("/movies/details/<movie_id>", methods=["GET"])
def get_movie_details(movie_id):
    pipeline = [
        {"$match": {"_id": movie_id}},
        {
            "$lookup": {
                "from": "genres",
                "localField": "genreIds",
                "foreignField": "_id",
                "as": "genres"
            }
        },
        {
            "$project": {
                "_id": 0,
                "movieId": "$_id",
                "title": 1,
                "description": 1,
                "type": 1,
                "releaseYear": 1,
                "averageRating": {"$ifNull": ["$averageRating", 0]},
                "genres": {
                    "$map": {
                        "input": "$genres",
                        "as": "g",
                        "in": {"name": "$$g.name"}
                    }
                }
            }
        }
    ]

    movie = list(db.movies.aggregate(pipeline))
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    movie[0]["views"] = db.watch_history.count_documents(
        {"movieId": movie_id}
    )
    return jsonify(movie[0])


@app.route("/movies/<movie_id>/like", methods=["POST"])
def toggle_like(movie_id):
    user_id = request.json.get("userId")
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    existing = db.likes.find_one({
        "userId": user_id,
        "movieId": movie_id
    })

    if existing:
        db.likes.delete_one({"_id": existing["_id"]})
        return jsonify({"liked": False})

    db.likes.insert_one({
        "userId": user_id,
        "movieId": movie_id,
        "createdAt": datetime.utcnow()
    })
    return jsonify({"liked": True})


@app.route("/movies/<movie_id>/like/<user_id>", methods=["GET"])
def is_movie_liked(movie_id, user_id):
    return jsonify({
        "liked": db.likes.find_one({
            "userId": user_id,
            "movieId": movie_id
        }) is not None
    })


@app.route("/movies/<movie_id>/watched", methods=["POST"])
def mark_movie_watched(movie_id):
    user_id = request.json.get("userId")
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    if db.watch_history.find_one({
        "userId": user_id,
        "movieId": movie_id
    }):
        return jsonify({"watched": True})

    db.watch_history.insert_one({
        "userId": user_id,
        "movieId": movie_id,
        "watchedAt": datetime.utcnow(),
        "source": "manual"
    })
    return jsonify({"watched": True})


@app.route("/movies/<movie_id>/watched/<user_id>", methods=["GET"])
def is_movie_watched(movie_id, user_id):
    return jsonify({
        "watched": db.watch_history.find_one({
            "userId": user_id,
            "movieId": movie_id
        }) is not None
    })


@app.route("/friends/follow", methods=["POST"])
def follow_user():
    data = request.json
    if data["userId"] == data["targetUserId"]:
        return jsonify({"error": "Cannot follow yourself"}), 400

    if not db.follows.find_one(data):
        db.follows.insert_one({
            **data,
            "createdAt": datetime.utcnow()
        })

    return jsonify({"following": True})


@app.route("/friends/unfollow", methods=["POST"])
def unfollow_user():
    data = request.json
    db.follows.delete_one({
        "userId": data["userId"],
        "followsUserId": data["targetUserId"]
    })
    return jsonify({"following": False})


@app.route("/friends/<user_id>", methods=["GET"])
def get_friends(user_id):
    pipeline = [
        {"$match": {"userId": user_id}},
        {
            "$lookup": {
                "from": "users",
                "localField": "followsUserId",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$project": {
                "_id": 0,
                "userId": "$user._id",
                "name": "$user.name",
                "country": "$user.country"
            }
        }
    ]
    return jsonify(list(db.follows.aggregate(pipeline)))


@app.route("/friends/suggestions/<user_id>", methods=["GET"])
def friend_suggestions(user_id):
    followed = db.follows.distinct(
        "followsUserId",
        {"userId": user_id}
    )

    users = db.users.find(
        {"_id": {"$nin": followed + [user_id]}},
        {"_id": 1, "name": 1, "country": 1}
    )
    return jsonify(list(users))


@app.route("/recommendations/friends/liked/<user_id>", methods=["GET"])
def recommend_from_friends_likes(user_id):
    pipeline = [
        {"$match": {"userId": user_id}},
        {
            "$lookup": {
                "from": "likes",
                "localField": "followsUserId",
                "foreignField": "userId",
                "as": "friendLikes"
            }
        },
        {"$unwind": "$friendLikes"},
        {
            "$lookup": {
                "from": "likes",
                "let": {"movieId": "$friendLikes.movieId"},
                "pipeline": [{
                    "$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$movieId", "$$movieId"]},
                                {"$eq": ["$userId", user_id]}
                            ]
                        }
                    }
                }],
                "as": "alreadyLiked"
            }
        },
        {"$match": {"alreadyLiked": {"$eq": []}}},
        {
            "$lookup": {
                "from": "watch_history",
                "let": {"movieId": "$friendLikes.movieId"},
                "pipeline": [{
                    "$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$movieId", "$$movieId"]},
                                {"$eq": ["$userId", user_id]}
                            ]
                        }
                    }
                }],
                "as": "alreadyWatched"
            }
        },
        {"$match": {"alreadyWatched": {"$eq": []}}},
        {
            "$lookup": {
                "from": "movies",
                "localField": "friendLikes.movieId",
                "foreignField": "_id",
                "as": "movie"
            }
        },
        {"$unwind": "$movie"},
        {
            "$lookup": {
                "from": "genres",
                "localField": "movie.genreIds",
                "foreignField": "_id",
                "as": "genres"
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": "$movie.title",
                "type": "$movie.type",
                "releaseYear": "$movie.releaseYear",
                "averageRating": {
                    "$ifNull": ["$movie.averageRating", 0]
                },
                "genres": {
                    "$map": {
                        "input": "$genres",
                        "as": "g",
                        "in": {"name": "$$g.name"}
                    }
                }
            }
        },
        {"$group": {"_id": "$title", "movie": {"$first": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": "$movie"}},
        {"$limit": 5}
    ]

    return jsonify({
        "userId": user_id,
        "recommendations": list(db.follows.aggregate(pipeline))
    })


if __name__ == "__main__":
    app.run(debug=True)

from pymongo import MongoClient

import os

# uri = "mongodb+srv://devlfaizankakar_db_user:<db_password>@rag.ivf6hpo.mongodb.net/?retryWrites=true&w=majority&appName=RAG"

# client = MongoClient(os.getenv("mongo_string"))
client = MongoClient("mongodb+srv://devlfaizankakar_db_user:JgOQooCv2N6gOSrp@rag.ivf6hpo.mongodb.net/?retryWrites=true&w=majority&appName=RAG")

db = client["mydatabase"]

users = db["users"]

sessions = db['sessions']

messages = db['messages']


# import os
# from pymongo import MongoClient

# # Correct connection string with db name
# uri = os.getenv("mongo_string")

# client = MongoClient(uri)

# db = client["mydatabase"]

# print(db.list_collection_names())


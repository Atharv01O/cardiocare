from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://atharvadevrukhkar13_db_user:atharv123@m0cluster.quzgmpk.mongodb.net/cardiocare?retryWrites=true&w=majority"
)

db = client["cardiocare"]

client.admin.command("ping")

print("MongoDB Connected")
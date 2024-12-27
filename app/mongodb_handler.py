from pymongo import MongoClient
import os


class MongoDBHandler:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
        self.db = self.client[os.getenv("MONGO_DB", "dota")]

    def get_collection(self, name):
        return self.db[name]

    def get_match(self, match_id):
        """Check if a match exists in the database."""
        return self.db.matches.find_one({"match_id": match_id})

    def save_match(self, match_data):
        """Save match data to the database."""
        self.db.matches.insert_one(match_data)

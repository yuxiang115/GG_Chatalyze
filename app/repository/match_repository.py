from pymongo import MongoClient
from app.configs.db_config import mongodb_client as mongo_client
import os


class MatchRepository:
    def __init__(self):
        self.client = mongo_client
        self.db = self.client[os.getenv("MONGO_DB_NAME", "gg_chatalyze")]

    def get_collection(self, name):
        return self.db[name]

    def get_match(self, match_id):
        """Check if a match exists in the database."""
        return self.db.matches.find_one({"match_id": match_id})

    def get_matches(self, match_ids):
        """Get matches from the database."""
        if not match_ids:
            return []
        match_ids = list(match_ids)
        return list(self.db.matches.find({"match_id": {"$in": match_ids}}))

    def save_match(self, match_data):
        """Save match data to the database."""
        self.db.matches.insert_one(match_data)

    def update_match(self, match_id, match_data):
        """Update match data in the database."""
        self.db.matches.update_one({"match_id": match_id}, {"$set": match_data}, upsert=True)

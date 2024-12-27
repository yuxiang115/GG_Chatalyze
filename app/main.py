import asyncio
import json

from discord_bot import DiscordBot
from dota_api import fetch_recent_matches, fetch_match_details
from mongodb_handler import MongoDBHandler
from llm_analysis import generate_analysis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import discordWebhook as discordWebhook
# 加载 .env 文件
load_dotenv()
# Environment variables
import os
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# MongoDB and collections
db = MongoDBHandler()
matches_collection = db.get_collection("matches")

# Function to refresh and fetch new match data
def refresh_matches():
    print("Refreshing matches...")
    player_ids = ["48645517"]  # Replace with real player IDs

    for player_id in player_ids:
        print(f"Fetching matches for player: {player_id}")
        # 如果 fetch_recent_matches 返回普通列表，不使用 await
        # recent_matches = fetch_recent_matches(player_id)
        recent_matches = [8099685034]
        print(f"Recent matches: {recent_matches}")

        for match_id in recent_matches:
            print(f"Checking if match {match_id} exists...")
            db_match = db.get_match(match_id)
            if not db_match:
                print(f"Fetching details for match {match_id}...")
                match_details = fetch_match_details(match_id)
                if match_details:
                    print(f"Saving match {match_id} to database...")
                    db.save_match(match_details)
            else:
                match_details = db_match
            print(f"Match details: {match_details}")
            analysis = generate_analysis(match_details)
            # bot.send_analysis_to_channel(analysis)
            discordWebhook.send(analysis)



# Initialize Discord bot
bot = DiscordBot()

# Main function
def main():
    # Schedule tasks
    refresh_matches()

if __name__ == "__main__":
    main()


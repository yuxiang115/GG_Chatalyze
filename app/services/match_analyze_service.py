import json

from app.services.open_dota_api_service import fetch_match_details
from . import dota_constants_service as dota_constants, llm_analysis_service as llm_analysis
from dotenv import load_dotenv
from app.discord import discordWebhook as discordWebhook
from app.repository.player_repository import fetch_player_with_most_recent_matches, fetch_all_players_id
from app.services.open_dota_api_service import fetch_recent_matches
from app.repository.match_repository import MatchRepository
# 加载 .env 文件
load_dotenv()
# Environment variables
import os
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# MongoDB and collections
match_repository = MatchRepository()
matches_collection = match_repository.get_collection("matches")


# Function to refresh and fetch new match data
def refresh_matches():
    print("Refreshing matches...")
    player_ids = fetch_all_players_id()

    recent_match_ids = []
    for player_id in player_ids:
        recent_match_ids += fetch_recent_matches(player_id)

    recent_match_ids = set(recent_match_ids)
    matches_db = match_repository.get_matches(recent_match_ids)
    matches_db_ids = [match["match_id"] for match in matches_db]
    matches_db_ids = set(matches_db_ids)
    recent_match_ids_not_in_db = recent_match_ids - matches_db_ids

    for match_id in recent_match_ids_not_in_db:
        match_details = fetch_match_details(match_id)
        if match_details:
            match_repository.save_match(match_details)
            dota_constants.fill_match_details(match_details)
            print(f"Match details: {json.dumps(match_details)}")
            analysis = llm_analysis.analyze(match_details)
            # bot.send_analysis_to_channel(analysis)
            content = [f'### Match ID: {match_id}'] + [message for message in analysis.values()]
            discordWebhook.send(content)

def analyze_match(match_id):
    matche_db = match_repository.get_match(match_id)
    match_detail = None
    if matche_db:
        del matche_db["_id"]
        match_detail = matche_db
    else:
        match_detail = fetch_match_details(match_id)
    if not match_detail:
        return None
    # deep copy the match_detail
    match_detail_original = json.loads(json.dumps(match_detail))
    dota_constants.fill_match_details(match_detail)
    if not matche_db:
        match_repository.save_match(match_detail_original)
    analysis = llm_analysis.analyze(match_detail)
    content =  [f'### Match ID: {match_id}'] + [message for message in analysis.values()]
    discordWebhook.send(content)
    return analysis




import json

from app.services.open_dota_api_service import fetch_match_details
from . import dota_constants_service as dota_constants, llm_analysis_service as llm_analysis
from dotenv import load_dotenv
from app.discord import discordWebhook as discordWebhook
from app.repository import player_repository
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

def auto_analyze_players_most_recent_matches():
    players_ids = player_repository.fetch_players_id_auto_analyze_enable()
    refresh_matches_by_player_ids(players_ids)


def refresh_matches():
    print("Refreshing matches...")
    player_ids = player_repository.fetch_all_players_id()
    refresh_matches_by_player_ids(player_ids)

# Function to refresh and fetch new match data
def refresh_matches_by_player_ids(player_ids: list, send_cache_analysis=False):
    recent_match_ids = []
    for player_id in player_ids:
        recent_match_ids += fetch_recent_matches(player_id)

    recent_match_ids = set(recent_match_ids)
    matches_db = match_repository.get_matches(recent_match_ids)
    matches_db = {match["match_id"]: match for match in matches_db}

    for match_id in recent_match_ids:
        if match_id in matches_db:
            if send_cache_analysis:
                analysis = matches_db[match_id]["analysis"]
                content = [f'### Match ID: {match_id}'] + [message for message in analysis.values()]
                discordWebhook.send(content)
            continue
        match_details = fetch_match_details(match_id)
        if match_details:
            dota_constants.fill_match_details(match_details)
            print(f"Match details: {json.dumps(match_details)}")
            analysis = llm_analysis.analyze(match_details)
            match_repository.save_match({"match_details": match_details, "match_id": match_id, "analysis": analysis})
            # bot.send_analysis_to_channel(analysis)
            content = [f'### Match ID: {match_id}'] + [message for message in analysis.values()]
            discordWebhook.send(content)

def analyze_match(match_id, use_cache_analysis=True):
    matche_db = match_repository.get_match(match_id)
    if matche_db:
        match_detail = matche_db["match_details"]
        analysis_db = matche_db["analysis"]
        if match_detail and use_cache_analysis:
            content = [f'### Match ID: {match_id}'] + [message for message in analysis_db.values()]
            discordWebhook.send(content)
            return analysis_db
    else:
        match_detail = fetch_match_details(match_id)
    if not match_detail:
        return None

    # deep copy the match_detail
    match_detail_original = json.loads(json.dumps(match_detail))
    dota_constants.fill_match_details(match_detail)

    analysis = llm_analysis.analyze(match_detail)

    if not matche_db:
        match_repository.save_match({"match_details": match_detail_original, "match_id": match_id, "analysis": analysis})
    content =  [f'### Match ID: {match_id}'] + [message for message in analysis.values()]
    discordWebhook.send(content)
    return analysis




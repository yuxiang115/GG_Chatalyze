import json

from app.services.open_dota_api_service import fetch_match_details
from app.services import dota_constants_service as dota_constants, llm_analysis_service as llm_analysis
from app.discord_util import discordWebhook as discordWebhook
from app.repository import player_repository
from app.services.open_dota_api_service import fetch_recent_matches
from app.repository.match_repository import MatchRepository

# MongoDB and collections
match_repository = MatchRepository()
matches_collection = match_repository.get_collection("matches")

def auto_analyze_players_most_recent_matches():
    players_ids = player_repository.fetch_players_id_auto_analyze_enable()
    refresh_matches_by_player_ids(players_ids)


# Function to refresh and fetch new match data
def refresh_matches_by_player_ids(player_ids: list, send_cache_analysis=False):
    recent_match_ids = []
    for player_id in player_ids:
        recent_match_ids += fetch_recent_matches(player_id)

    recent_match_ids = set(recent_match_ids)
    matches_db = match_repository.get_matches(recent_match_ids)
    matches_db = {match["match_id"]: match for match in matches_db}

    result = []

    for match_id in recent_match_ids:
        if match_id in matches_db:
            analysis = matches_db[match_id]["analysis"]
            result.append({'match_detail': dota_constants.fill_match_details(matches_db[match_id]['match_details']), 'analysis': analysis})
            if send_cache_analysis:
                content = [f'### Match ID: {match_id}'] + [message for message in analysis.values()]
                discordWebhook.send(content)
            continue
        match_details = fetch_match_details(match_id)
        if match_details:
            match_detail_original = json.loads(json.dumps(match_details))
            match_details = dota_constants.fill_match_details(match_details)
            print(f"Match details: {json.dumps(match_details)}")
            analysis = llm_analysis.analyze(match_details)
            match_repository.save_match({"match_details": match_detail_original, "match_id": match_id, "analysis": analysis})
            # bot.send_analysis_to_channel(analysis)
            content = [f'### Match ID: {match_id}'] + [message for message in analysis.values()]
            discordWebhook.send(content)
            result.append({'match_detail': match_details, 'analysis': analysis})
    return result

def analyze_match(match_id, use_cache_analysis=True, send_cache_analysis=False):
    matche_db = match_repository.get_match(match_id)
    if matche_db:
        match_detail = matche_db["match_details"]
        analysis_db = matche_db["analysis"]
        if match_detail and use_cache_analysis:
            content = [f'### Match ID: {match_id}'] + [message for message in analysis_db.values()]
            if send_cache_analysis:
                discordWebhook.send(content)
            return {'match_detail': dota_constants.fill_match_details(match_detail), 'analysis': analysis_db}
    else:
        match_detail = fetch_match_details(match_id)
    if not match_detail:
        return None

    # deep copy the match_detail
    match_detail_original = json.loads(json.dumps(match_detail))
    match_detail = dota_constants.fill_match_details(match_detail)

    analysis = llm_analysis.analyze(match_detail)
    if not matche_db:
        match_repository.save_match({"match_details": match_detail_original, "match_id": match_id, "analysis": analysis})
        content = [f'### Match ID: {match_id}'] + [message for message in analysis.values()]
        discordWebhook.send(content)
    return {'match_detail': match_detail, 'analysis': analysis}

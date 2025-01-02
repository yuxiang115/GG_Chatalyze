from fastapi import APIRouter
from app.services import match_analyze_service
from app.services.open_dota_api_service import fetch_player
from app.repository import player_repository
from datetime import datetime, timedelta
# 创建 APIRouter 实例
player_router = APIRouter()

@player_router.put("/")
def update_player(data: dict):
    player_id = data.get("player_id")
    discord_id = data.get("discord_id", None)
    player = fetch_player(player_id)
    personal_name = None
    if player:
        personal_name = player.get("profile", {}).get("personaname", None)
    res = player_repository.put_player(player_id, personal_name, discord_id)
    return res

@player_router.get("/enableAutoAnalyze/{player_id}")
def enable_auto_analyze(player_id: str, hours: int = 0, discord_id: str = None):
    if not hours or not isinstance(hours, int) or hours < 1:
        return {"message": "Invalid hours! Please provide a valid hours value! (hours > 0)"}
    player_db = player_repository.get_player(player_id)
    if not player_db:
        player = fetch_player(player_id)
        if not player:
            return {"message": "Player not found!"}
        personal_name = player.get("profile", {}).get("personaname", None)
    else:
        personal_name = player_db.get("personal_name", None)
        discord_id = player_db.get("discord_id", discord_id)

    auto_analyze_end_datetime = datetime.now() + timedelta(hours=hours)
    auto_analyze_end_datetime_str = auto_analyze_end_datetime.strftime('%Y-%m-%d %H:%M:%S')
    res = player_repository.put_player(player_id, personal_name, discord_id, auto_analyze_end_datetime_str)
    return res


@player_router.get("/analyzeMostRecentlyMatch/{player_id}")
def analyze_most_recently_match(player_id: int):
    match_analyze_service.refresh_matches_by_player_ids([player_id], send_cache_analysis=True)
    return {"message": "Analysis started!"}


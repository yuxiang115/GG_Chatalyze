from fastapi import APIRouter
from app.services import match_analyze_service
from app.services.open_dota_api_service import fetch_player
from app.repository.player_repository import put_player
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
    res = put_player(player_id, personal_name, discord_id)
    return res


@player_router.get("/refresh")
def refresh_matches():
    match_analyze_service.refresh_matches()
    return {"message": "Matches refreshed!"}

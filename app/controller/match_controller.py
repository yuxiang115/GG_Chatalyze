from fastapi import APIRouter
from app.services import match_analyze_service
# 创建 APIRouter 实例
match_router = APIRouter()

@match_router.get("/analyze/{match_id}")
def analyze_match(match_id: int):
    res = match_analyze_service.analyze_match(match_id)
    return res

@match_router.get("/refresh")
def refresh_matches():
    match_analyze_service.refresh_matches()
    return {"message": "Matches refreshed!"}

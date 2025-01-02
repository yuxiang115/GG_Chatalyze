from fastapi import APIRouter
from app.services import match_analyze_service
# 创建 APIRouter 实例
match_router = APIRouter()

@match_router.get("/analyze/{match_id}")
def analyze_match(match_id: int, use_cache_analysis: bool = True):
    res = match_analyze_service.analyze_match(match_id, use_cache_analysis)
    return res


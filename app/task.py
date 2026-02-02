import time
from app.services import match_analyze_service
def refresh_matches():
    """刷新比赛数据的计划任务"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 正在刷新比赛数据并且分析...")
    match_analyze_service.auto_analyze_players_most_recent_matches()


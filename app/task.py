import time
from app.services.match_analyze_service import refresh_matches as refresh_matches_analyze
def refresh_matches():
    """刷新比赛数据的计划任务"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 正在刷新比赛数据并且分析...")
    refresh_matches_analyze()


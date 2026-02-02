from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.task import refresh_matches

def create_scheduler():
    """创建并配置 APScheduler 调度器"""
    scheduler = BackgroundScheduler()

    # 添加任务 1：每 10 秒刷新比赛数据
    scheduler.add_job(
        refresh_matches,
        trigger=IntervalTrigger(minutes=2),
        id="refresh_matches",
        replace_existing=True,
    )


    return scheduler

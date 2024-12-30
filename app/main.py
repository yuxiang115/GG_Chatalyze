from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.controller.match_controller import match_router
from app.controller.player_controller import player_router
from scheduler.scheduler import create_scheduler
import uvicorn

# 初始化调度器
scheduler = create_scheduler()

# 使用 lifespan 替代 on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """管理应用的生命周期"""
    print("Starting scheduler...")
    scheduler.start()  # 启动调度器
    yield  # 在这里可以执行应用运行时的其他初始化
    print("Shutting down scheduler...")
    scheduler.shutdown()  # 关闭调度器

app = FastAPI(lifespan=lifespan)

app.include_router(match_router, prefix="/match")
app.include_router(player_router, prefix="/player")
@app.get("/")
def read_root():
    return {"message": "FastAPI with lifespan and multiple controllers!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

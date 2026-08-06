"""FastAPI 入口

只做三件事：
1. 创建 FastAPI app 实例
2. 生命周期管理（startup / shutdown）
3. 注册路由模块

不在此文件定义任何路由函数。
"""

import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.services.matlab import MatlabExecutor
from app.core.job_manager import JobManager
from app.core.websocket import connection_manager, broadcast_loop

# API v1 路由模块
from app.api import (
    health,
    jobs,
    ws,
    callback as callback_route,
    evaluate as evaluate_route,
)

logger = logging.getLogger(__name__)

# 全局实例（startup 时初始化）
executor: MatlabExecutor | None = None
job_manager: JobManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global executor, job_manager

    # ── startup ──
    executor = MatlabExecutor()
    await executor.start()

    job_manager = JobManager(executor)
    await job_manager.start()

    # 注入依赖到各路由模块
    health.init(executor)
    jobs.init(job_manager)
    callback_route.init(job_manager)
    evaluate_route.init(job_manager, config.matlab_root)

    # 启动后台广播协程
    broadcast_task = asyncio.create_task(broadcast_loop(connection_manager))

    yield

    # ── shutdown ──
    broadcast_task.cancel()
    try:
        await broadcast_task
    except asyncio.CancelledError:
        pass

    if job_manager:
        await job_manager.stop()
    if executor:
        await executor.stop()


app = FastAPI(
    title="梯级水库多目标优化调度 API",
    version="1.0.0",
    lifespan=lifespan,
    description="龙羊峡—刘家峡梯级水库 NSGA-II / PAEM 多目标优化调度模型 Web 服务",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API v1 路由
app.include_router(health.router)            # GET /health
app.include_router(jobs.router)              # POST /run, GET /status, /jobs, /results, /process
app.include_router(ws.router)                # WS /ws/{job_id}
app.include_router(callback_route.router)    # POST /cb
app.include_router(evaluate_route.router, prefix="/evaluate")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=False,
        log_level="info",
    )

"""健康检查端点"""

from fastapi import APIRouter

from app.schemas.result import HealthResponse

router = APIRouter()

# 由 main.py lifespan 注入
_executor_ref = None


def init(executor) -> None:
    """注入 MatlabExecutor 引用"""
    global _executor_ref
    _executor_ref = executor


@router.get("/health", response_model=HealthResponse)
async def health():
    """健康检查端点"""
    engine_ready = (
        _executor_ref is not None
        and hasattr(_executor_ref, "is_alive")
        and _executor_ref.is_alive()
    )
    return HealthResponse(
        status="ok",
        engine="ready" if engine_ready else "not started",
        version="1.0.0",
    )

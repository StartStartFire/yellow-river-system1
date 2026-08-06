"""MATLAB 回调端点

接收 MATLAB 通过 webwrite 推送的进度数据和过程数据。
"""

import logging

from fastapi import APIRouter

from app.schemas.callback import CallbackPayload, CallbackResponse
from app.core.callback import callback_queue, build_envelope, extract_job_id_from_data

logger = logging.getLogger(__name__)

router = APIRouter()

# 由 main.py lifespan 注入
_job_manager = None


def init(job_manager) -> None:
    """注入 JobManager 引用"""
    global _job_manager
    _job_manager = job_manager


@router.post("/cb", response_model=CallbackResponse)
async def callback(payload: CallbackPayload):
    """MATLAB 回调入口

    接收两种 type：
    - 'progress': 汇总指标 → WebSocket 实时推送
    - 'process_data': 过程数据 → WebSocket 推送 + 存储供 GET /process 补拉
    """
    cb_job_id = extract_job_id_from_data(payload.data)
    if not cb_job_id and _job_manager:
        cb_job_id = _job_manager.current_job_id

    if payload.type == "progress":
        # 汇总指标 → WebSocket 实时推送
        envelope = build_envelope(payload, job_id=cb_job_id)
        await callback_queue.put(envelope)

    elif payload.type == "process_data":
        # 过程数据 → 存储到后端供补拉
        if _job_manager and cb_job_id:
            record = _job_manager.get_status(cb_job_id)
            if record:
                record.process_data = payload.data
        # 同时也推送到 WebSocket
        envelope = build_envelope(payload, job_id=cb_job_id)
        await callback_queue.put(envelope)

    else:
        logger.warning("未知回调类型: %s", payload.type)

    logger.debug("收到回调: type=%s, job_id=%s", payload.type, cb_job_id)
    return CallbackResponse(received=True, job_id=cb_job_id)

"""MATLAB 回调接收

接收 MATLAB 通过 webwrite POST 到 /cb 的推送数据。
Pydantic 校验后写入 asyncio.Queue，供 WebSocket 广播循环消费。
"""

import asyncio
import logging
from datetime import datetime, timezone

from app.schemas.callback import CallbackPayload

logger = logging.getLogger(__name__)


class CallbackQueue:
    """回调消息缓冲区

    封装 asyncio.Queue，callback.py 生产者写入，
    websocket.py 广播循环消费。
    """

    def __init__(self, maxsize: int = 1000):
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)

    async def put(self, msg: dict):
        """写入一条消息（非阻塞，队列满时丢弃最旧消息）"""
        try:
            self._queue.put_nowait(msg)
        except asyncio.QueueFull:
            # 队列满时丢弃最旧消息，确保回调不阻塞
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(msg)
            except asyncio.QueueEmpty:
                pass

    async def get(self) -> dict:
        """取出一条消息（阻塞）"""
        return await self._queue.get()

    def qsize(self) -> int:
        """当前队列长度"""
        return self._queue.qsize()


def build_envelope(
    cb_payload: CallbackPayload,
    job_id: str | None = None,
) -> dict:
    """将回调载荷包装为 WebSocket 广播信封格式

    输入:
        cb_payload: MATLAB 回调的原始数据
        job_id: 任务 ID（从 data 中提取或显式传入）

    输出:
        符合 WS 消息协议的 dict:
        {
            "type": "progress",
            "job_id": "...",
            "timestamp": "...",
            "payload": { ... }
        }
    """
    data = cb_payload.data or {}

    # 从 data 中提取 timestamp，或使用当前时间
    timestamp = data.get("timestamp")
    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "type": cb_payload.type,
        "job_id": job_id or data.get("job_id", "unknown"),
        "timestamp": timestamp,
        "payload": data,
    }


def extract_job_id_from_data(data: dict) -> str | None:
    """尝试从回调 data 中提取 job_id"""
    return data.get("job_id") if isinstance(data, dict) else None


# 全局单例
callback_queue = CallbackQueue()

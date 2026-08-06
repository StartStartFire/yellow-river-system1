"""WebSocket 广播

连接管理 + 从 CallbackQueue 消费并广播给所有订阅客户端。
"""

import asyncio
import json
import logging
from fastapi import WebSocket

from app.core.callback import callback_queue

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器

    按 job_id 分组管理连接：
    - connect(ws, job_id): 注册连接
    - disconnect(ws, job_id): 移除连接
    - broadcast(job_id, message): 向该 job 的所有客户端广播
    """

    def __init__(self):
        # { job_id: set[WebSocket] }
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, ws: WebSocket, job_id: str):
        """接受 WebSocket 连接并注册"""
        await ws.accept()
        if job_id not in self._connections:
            self._connections[job_id] = set()
        self._connections[job_id].add(ws)
        logger.info("WebSocket 客户端连接: job_id=%s, 当前连接数=%d",
                     job_id, len(self._connections[job_id]))

    def disconnect(self, ws: WebSocket, job_id: str):
        """移除 WebSocket 连接"""
        if job_id in self._connections:
            self._connections[job_id].discard(ws)
            if not self._connections[job_id]:
                del self._connections[job_id]
        logger.info("WebSocket 客户端断开: job_id=%s", job_id)

    async def broadcast(self, job_id: str, message: dict):
        """向指定 job 的所有订阅客户端广播消息

        发送失败（连接断开）时自动移除该连接。
        """
        if job_id not in self._connections:
            return

        disconnected: list[WebSocket] = []
        for ws in self._connections[job_id]:
            try:
                await ws.send_json(message)
            except Exception:
                # 客户端断开是预期行为，静默清理
                disconnected.append(ws)

        # 清理已断开的连接
        for ws in disconnected:
            self.disconnect(ws, job_id)

    @property
    def active_connections(self) -> int:
        """当前活跃连接总数"""
        return sum(len(conns) for conns in self._connections.values())

    def get_job_ids(self) -> list[str]:
        """获取有活跃连接的所有 job_id"""
        return list(self._connections.keys())


async def broadcast_loop(manager: ConnectionManager):
    """后台广播循环

    从 CallbackQueue 消费消息，根据 job_id 广播给对应订阅客户端。
    """
    while True:
        try:
            envelope = await callback_queue.get()
            job_id = envelope.get("job_id", "unknown")
            await manager.broadcast(job_id, envelope)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning("广播循环异常: %s", e, exc_info=True)
            await asyncio.sleep(0.1)


# 全局单例
connection_manager = ConnectionManager()

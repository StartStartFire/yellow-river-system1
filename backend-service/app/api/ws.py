"""WebSocket 实时订阅端点"""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.websocket import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{job_id}")
async def websocket_endpoint(ws: WebSocket, job_id: str):
    """WebSocket 实时订阅端点

    客户端连接后，会收到该 job_id 的 progress/log/status 消息。
    """
    await connection_manager.connect(ws, job_id)
    try:
        # 保持连接，等待客户端断开
        while True:
            # 可以接收客户端发来的消息（如 ping 保持心跳）
            await ws.receive_text()
    except WebSocketDisconnect:
        # 客户端主动断开 — 正常行为
        pass
    except Exception as e:
        logger.warning("WebSocket 连接异常: job_id=%s, error=%s", job_id, e)
    finally:
        connection_manager.disconnect(ws, job_id)

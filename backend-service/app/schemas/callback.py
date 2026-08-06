"""回调相关数据模型"""

from pydantic import BaseModel


class CallbackPayload(BaseModel):
    """MATLAB 回调推送的顶层结构校验"""
    type: str  # 'progress'
    data: dict  # 具体的进度数据

class CallbackResponse(BaseModel):
    """/cb 端点返回确认"""
    received: bool
    job_id: str | None = None

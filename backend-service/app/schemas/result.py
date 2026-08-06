"""结果相关响应模型"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """GET /health 响应"""
    status: str
    engine: str
    version: str


class ResultResponse(BaseModel):
    """GET /results/{job_id} 响应

    chromosome 矩阵每行包含：
    - 1~V: 决策变量（龙羊峡+刘家峡逐时段水位）
    - V+1~V+M: 目标函数值
    - V+M+1: 非支配排序等级
    - V+M+2: 拥挤距离

    evaluating 矩阵为 pop × 22 的评价指标矩阵（用于评价系统排名）。

    Inf/NaN 值被转换为 null 以兼容 JSON 序列化。
    """
    job_id: str
    status: str
    algorithm: str
    chromosome: list[list[float | None]] | None = None
    evaluating: list[list[float | None]] | None = None
    objective_names: list[str] = ["缺水量", "发电量", "协同度"]
    message: str | None = None
    generated_at: str | None = None

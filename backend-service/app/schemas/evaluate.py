"""评价系统相关请求/响应模型"""

from pydantic import BaseModel, Field


class EvaluateRequest(BaseModel):
    """POST /evaluate 请求体"""
    job_id: str = Field(description="优化任务 ID")
    method: str = Field(
        default="ALL",
        pattern=r"^(NMF|PP|AHP_FUZZY|ALL)$",
        description="评价方法: NMF / PP / AHP_FUZZY / ALL"
    )


class EvaluateResponse(BaseModel):
    """POST /evaluate 响应"""
    job_id: str
    method: str
    status: str  # success | error
    message: str | None = None
    ranking: list[int] | None = None  # 0-based 排名（0 为最优）
    scores: list[float] | None = None  # 各方案得分
    best_scheme_index: int | None = None  # 最优方案索引（0-based）
    details: dict | None = None  # 算法返回的完整详情

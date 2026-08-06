"""任务相关请求/响应模型"""

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    """POST /run 请求体"""
    algorithm: str = Field(default="nsga2", pattern=r"^(nsga2|paem)$")
    pop: int = Field(default=15, ge=1, description="种群大小")
    iterate: int = Field(default=20, ge=1, description="进化代数")
    M: int = Field(default=2, ge=1, description="目标函数个数")
    Q_sediment: float = Field(default=1800.0, ge=0.0, description="调沙流量")
    K_mut: int | None = Field(default=None, ge=0, description="PAEM 变异参数")
    crossover_rate: float = Field(default=0.9, ge=0.0, le=1.0, description="交叉概率 Pc")
    flag_xixian: str = Field(default="全无", pattern=r"^(全无|全有|有上无下|有下无上)$", description="西线调水方案")
    # 年份范围（可选，不传时使用 Excel 全部年份）
    year_start: int | None = Field(default=None, ge=1970, le=2023, description="调度起始年份")
    year_end: int | None = Field(default=None, ge=1970, le=2023, description="调度结束年份")
    # 约束参数（可选，不传时使用 MATLAB 代码中的默认值）
    initial_water_level_longyangxia: float | None = Field(default=None, description="龙羊峡起调水位(m)")
    initial_water_level_liujiaxia: float | None = Field(default=None, description="刘家峡起调水位(m)")
    ice_prevention_flows: list[float] | None = Field(default=None, description="防凌流量 [11月,12月,1月,2月,3月](m³/s)")


class JobStatusResponse(BaseModel):
    """GET /status/{id} 响应"""
    job_id: str
    status: str  # queued | running | completed | failed
    progress_percent: float | None = None
    created_at: str | None = None
    message: str | None = None


class JobSummary(BaseModel):
    """任务列表中的摘要信息"""
    job_id: str
    status: str
    algorithm: str
    progress_percent: float | None = None
    created_at: str | None = None

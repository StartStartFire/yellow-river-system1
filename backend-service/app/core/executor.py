"""任务执行器抽象接口

定义 BaseExecutor 抽象基类，独立于具体实现。
job_manager 通过此接口执行任务，不直接依赖 MATLAB。
生产使用 MatlabExecutor（app.services.matlab）。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TaskConfig:
    """优化任务参数配置"""
    algorithm: str  # 'nsga2' | 'paem'
    pop: int
    iterate: int
    M: int
    Q_sediment: float
    K_mut: int | None = None  # PAEM 专用
    crossover_rate: float = 0.9  # 交叉概率 Pc
    flag_xixian: str = "全无"    # 西线调水
    year_start: int | None = None  # 调度起始年份，None 表示使用全部年份
    year_end: int | None = None    # 调度结束年份，None 表示使用全部年份
    job_id: str = ""  # 任务标识
    # 约束参数（起调水位、防凌流量）
    initial_water_level_longyangxia: float | None = None  # 龙羊峡起调水位，默认 2580
    initial_water_level_liujiaxia: float | None = None    # 刘家峡起调水位，默认 1720
    ice_prevention_flows: list[float] | None = None        # 防凌流量 [11月,12月,1月,2月,3月]，默认 [610,420,420,420,420]


@dataclass
class TaskResult:
    """优化任务执行结果

    实际数据通过 JSONL 文件持久化，result 仅含摘要信息。
    """
    job_id: str = ""
    success: bool = True
    message: str = ""
    chromosome: list = field(default_factory=list)
    evaluating: list = field(default_factory=list)  # 22项评价指标矩阵
    plan_details: list = field(default_factory=list)  # 每个种群个体的决策分析明细
    completed_at: str = ""


class BaseExecutor(ABC):
    """任务执行器抽象基类"""

    @abstractmethod
    async def start(self):
        """初始化执行器（启动引擎、加载数据）"""
        ...

    @abstractmethod
    async def run(self, task: TaskConfig) -> TaskResult:
        """执行一次优化任务"""
        ...

    @abstractmethod
    async def stop(self):
        """关闭执行器，释放资源"""
        ...


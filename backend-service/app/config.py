"""全局配置（dataclass 单例）

所有可变参数收拢到此文件。
原型阶段直接修改本文件即可变更配置。
"""

from dataclasses import dataclass
from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
"""项目根目录 = backend-service/app/config.py 向上 3 级 → yellow_river_project/"""


@dataclass
class Config:
    """所有可变参数收拢到此类。

    matlab_root 自动基于项目根目录计算，换机器无需修改。
    """

    # 服务器
    host: str = "127.0.0.1"
    port: int = 18080

    # CORS（允许的前端 origin 列表）
    cors_origins: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.cors_origins is None:
            self.cors_origins = [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ]

    # MATLAB 路径（自动基于项目根目录计算，换机器无需修改）
    @property
    def matlab_root(self) -> str:
        return str(_PROJECT_ROOT / "matlab-model")

    data_file: str = "data.xlsx"

    # 回调
    callback_host: str = "127.0.0.1"
    callback_port: int = 18080
    callback_timeout: float = 1.0

    @property
    def callback_url(self) -> str:
        return f"http://{self.callback_host}:{self.callback_port}/cb"

    # 默认任务参数
    default_pop: int = 15
    default_iterate: int = 20
    default_m: int = 2
    default_q_sediment: float = 1800.0
    default_k_mut: int = 50


# 全局单例
config = Config()

"""MATLAB Engine 服务封装

通过 matlab.engine 调用 NSGA-II / PAEM 优化模型。
所有 Engine 操作在单线程中串行执行（非线程安全）。
"""

import asyncio
import logging
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any

import matlab.engine

from app.config import config
from app.core.executor import BaseExecutor, TaskConfig, TaskResult

logger = logging.getLogger(__name__)


def _sanitize_matlab_value(value: Any) -> Any:
    """将 MATLAB 矩阵中的 Inf/NaN 转为 None，兼容 JSON 序列化。

    MATLAB 的 double 矩阵可能包含 Inf/-Inf/NaN，
    Pydantic 无法序列化这些特殊浮点值，需要提前清洗。
    """
    if isinstance(value, (int, float)):
        if math.isinf(value) or math.isnan(value):
            return None
        return value
    return value


class MatlabExecutor(BaseExecutor):
    """MATLAB Engine 任务执行器

    通过 matlab.engine 调用 NSGA-II / PAEM 优化模型。
    所有 Engine 操作在单线程中串行执行。
    """

    def __init__(self, cfg: Any = None):
        self._cfg = cfg or config
        self._eng: matlab.engine.MatlabEngine | None = None
        self._pool: ThreadPoolExecutor | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    async def start(self):
        """启动 MATLAB Engine 并加载数据"""
        self._loop = asyncio.get_running_loop()
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="matlab")

        logger.info("正在启动 MATLAB Engine ...")
        await self._run_in_engine_thread(self._start_engine_sync)
        logger.info("MATLAB Engine 启动成功")

    async def run(self, task: TaskConfig) -> TaskResult:
        """执行一次优化任务"""
        if self._eng is None:
            return TaskResult(
                job_id=task.job_id,
                success=False,
                message="Engine 未就绪",
            )

        logger.info(
            "开始执行任务 %s: algorithm=%s, pop=%d, iterate=%d, M=%d",
            task.job_id[:8], task.algorithm, task.pop, task.iterate, task.M,
        )

        try:
            chromosome, evaluating = await self._run_in_engine_thread(
                self._run_optimization_sync, task
            )
            return TaskResult(
                job_id=task.job_id,
                success=True,
                message=f"{task.algorithm.upper()} 优化完成",
                chromosome=chromosome,
                evaluating=evaluating,
                completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception as e:
            logger.error("任务 %s 执行失败: %s", task.job_id[:8], str(e))
            return TaskResult(
                job_id=task.job_id,
                success=False,
                message=f"执行失败: {str(e)}",
                completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            )

    async def stop(self):
        """关闭 MATLAB Engine"""
        if self._eng:
            logger.info("正在关闭 MATLAB Engine ...")
            try:
                await self._run_in_engine_thread(self._stop_engine_sync)
            except Exception as e:
                logger.warning("关闭 Engine 时出错: %s", e)
            self._eng = None

        if self._pool:
            self._pool.shutdown(wait=False)
            self._pool = None

        logger.info("MATLAB Engine 已关闭")

    def is_alive(self) -> bool:
        """Engine 是否正在运行"""
        return self._eng is not None

    # ─── 同步方法（在 Engine 线程中执行） ─────────────────

    def _start_engine_sync(self):
        """同步启动 Engine（在后台线程中执行）

        数据加载延迟到每次优化任务执行时，
        由 _run_optimization_sync 中的 load_data 按任务参数加载。
        """
        self._eng = matlab.engine.start_matlab()
        self._eng.cd(self._cfg.matlab_root)

    def _stop_engine_sync(self):
        """同步关闭 Engine（在后台线程中执行）"""
        if self._eng:
            self._eng.quit()
            self._eng = None

    def _run_optimization_sync(self, task: TaskConfig) -> tuple[list, list]:
        """同步执行优化（在后台线程中执行）

        根据西线调水参数重载数据，然后调用 nsga_2_para 或 PAEM_para。
        返回 (chromosome, evaluating) 两个矩阵。
        """
        # 设置年份范围（可选，必须在 load_data 之前设置，供截取逻辑使用）
        if task.year_start is not None and task.year_end is not None:
            if task.year_start > task.year_end:
                raise ValueError(f"year_start ({task.year_start}) 必须小于 year_end ({task.year_end})")
            logger.info("设置年份范围: %d ~ %d", task.year_start, task.year_end)
            self._eng.eval(
                f"global YEAR_START YEAR_END; "
                f"YEAR_START = {int(task.year_start)}; "
                f"YEAR_END = {int(task.year_end)};",
                nargout=0,
            )
        else:
            logger.debug("未设置年份范围，使用 Excel 全部年份")
            self._eng.eval("global YEAR_START YEAR_END; YEAR_START = []; YEAR_END = [];", nargout=0)

        # 根据任务参数重载数据（flag_xixian 运行时动态传入）
        self._eng.load_data(self._cfg.data_file, task.flag_xixian, nargout=0)

        # 设置全局变量 Q_sediment（供 evaluate_objective_save_info 使用）
        self._eng.eval(f"global Q_sediment; Q_sediment = {float(task.Q_sediment)};", nargout=0)

        # 设置约束参数全局变量（起调水位、防凌流量）
        if task.initial_water_level_longyangxia is not None:
            self._eng.eval(f"global LONG_Z_INI_VAL; LONG_Z_INI_VAL = {float(task.initial_water_level_longyangxia)};", nargout=0)
        if task.initial_water_level_liujiaxia is not None:
            self._eng.eval(f"global LIU_Z_INI_VAL; LIU_Z_INI_VAL = {float(task.initial_water_level_liujiaxia)};", nargout=0)
        if task.ice_prevention_flows is not None and len(task.ice_prevention_flows) == 5:
            flows_str = ",".join(str(float(v)) for v in task.ice_prevention_flows)
            self._eng.eval(f"global QMIN_VAL; QMIN_VAL = [{flows_str}];", nargout=0)

        if task.algorithm == "nsga2":
            result = self._eng.nsga_2_para(
                float(task.pop),
                float(task.iterate),
                float(task.M),
                float(task.Q_sediment),
                float(task.crossover_rate),
                nargout=1,
            )
        elif task.algorithm == "paem":
            if task.K_mut is None:
                raise ValueError("PAEM 算法需要提供 K_mut 参数")
            result = self._eng.PAEM_para(
                float(task.pop),
                float(task.iterate),
                float(task.K_mut),
                float(task.M),
                float(task.Q_sediment),
                float(task.crossover_rate),
                nargout=1,
            )
        else:
            raise ValueError(f"不支持的算法: {task.algorithm}")

        # 将 MATLAB 返回的 dict 中的 chromosome 转为 Python list
        # 同时提取 evaluating 矩阵
        logger.debug("MATLAB result keys: %s", list(result.keys()) if isinstance(result, dict) else type(result))
        chromo = self._extract_chromosome(result)
        eval_data = self._extract_evaluating(result)
        return chromo, eval_data

    def _extract_chromosome(self, result: dict) -> list:
        """从 MATLAB 返回结果中提取 chromosome 矩阵

        NSGA-II 返回字段名 'chromosome'（含决策变量 + 目标值 + rank + 拥挤距离）
        PAEM 返回字段名 'chromosome_acc'（精确评估后的目标值）

        注意：MATLAB 矩阵可能包含 Inf/NaN，需要过滤为 None，
        Pydantic 序列化时将转为 JSON 的 null。
        """
        if not isinstance(result, dict):
            return []

        for key in ("chromosome", "chromosome_acc"):
            if key in result:
                chrom = result[key]
                raw = chrom.tolist() if hasattr(chrom, "tolist") else list(chrom)
                return [[_sanitize_matlab_value(v) for v in row] for row in raw]
        return []

    def _extract_evaluating(self, result: dict) -> list:
        """从 MATLAB 返回结果中提取 evaluating 评价指标矩阵（pop × 22）

        MATLAB Engine 返回的 MatLabStruct 不支持 .get()，
        必须用 in 运算符判断字段是否存在。
        """
        if not isinstance(result, dict):
            return []

        if "evaluating" not in result:
            return []
        evaluating = result["evaluating"]
        if evaluating is not None:
            raw = evaluating.tolist() if hasattr(evaluating, "tolist") else list(evaluating)
            return [[_sanitize_matlab_value(v) for v in row] for row in raw]
        return []

    # ─── 异步工具 ────────────────────────────────────────

    async def _run_in_engine_thread(self, func: callable, *args: Any, **kwargs: Any) -> Any:
        """在 Engine 专用线程中执行同步函数"""
        if self._pool is None:
            raise RuntimeError("Executor 未启动")
        return await self._loop.run_in_executor(self._pool, func, *args, **kwargs)

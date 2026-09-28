"""水沙耦合模型服务封装

通过子进程调用 river_model/run_model_service.py，运行水沙统一调度 +
河道水文水动力演变 + 输沙造床的时空耦合模型（确定性洪水仿真）。

与 MatlabExecutor 的区别：
- 水沙是**确定性仿真**（给定重现期→一套结果），无 evaluating 矩阵，不参与多算法评价；
- 通过 asyncio.create_subprocess_exec 启动独立子进程（模型有全局状态，需进程隔离）；
- 模型运行期间通过 run_model_service._cb_push 向 /cb 实时推送 progress/process_data，
  经现有回调链路→WebSocket 推送前端；结果写 result_file，本执行器读取后返回 TaskResult。

设计要点：
- 模型单次约 160 秒，需超时保护；
- 结果 JSON 以 --result_file 落盘（比解析 stdout 更可靠，后者混有模型 print 输出）；
- 进程结束返回码非 0 或超时视为失败，静默降级为 TaskResult(success=False)。
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any

from app.config import config
from app.core.executor import BaseExecutor, TaskConfig, TaskResult

logger = logging.getLogger(__name__)


class WaterSedimentExecutor(BaseExecutor):
    """水沙耦合模型任务执行器

    以子进程方式运行 run_model_service.py。
    """

    def __init__(self, cfg: Any = None):
        self._cfg = cfg or config

    async def start(self):
        """水沙模型无需常驻进程，start 为空操作。

        子进程在每次 run() 时创建，避免模型全局状态留存。
        """
        logger.info("WaterSedimentExecutor 就绪（无常驻进程，子进程按任务创建）")

    async def run(self, task: TaskConfig) -> TaskResult:
        """执行一次水沙仿真任务"""
        script = self._cfg.river_model_service_script
        if not os.path.exists(script):
            logger.error("水沙模型服务脚本不存在: %s", script)
            return TaskResult(
                job_id=task.job_id,
                success=False,
                message=f"水沙模型服务脚本不存在: {script}",
                completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            )

        cb_url = f"http://{self._cfg.callback_host}:{self._cfg.callback_port}/cb"
        result_file = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, prefix=f"ws_{task.job_id[:8]}_"
        ).name

        python = os.environ.get("RIVER_PYTHON")
        if not python:
            python = sys.executable
        logger.info("水沙模型 python: %s", python)

        cmd = [
            python,
            script,
            "--flood_frequency", task.flood_frequency,
            "--job_id", task.job_id,
            "--cb_url", cb_url,
            "--result_file", result_file,
        ]

        logger.info(
            "开始水沙任务 %s: frequency=%s, cb_url=%s",
            task.job_id[:8], task.flood_frequency, cb_url,
        )

        proc: asyncio.subprocess.Process | None = None
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # 模型单次约 160 秒，给出充足超时（默认 600s）
            timeout = float(os.environ.get("RIVER_TIMEOUT", "600"))
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

            if proc.returncode != 0:
                err_tail = (stderr.decode("utf-8", errors="replace") or "")[-2000:]
                logger.error("水沙子进程退出码 %s: %s", proc.returncode, err_tail)
                return TaskResult(
                    job_id=task.job_id,
                    success=False,
                    message=f"水沙模型运行失败（退出码 {proc.returncode}）: {err_tail}",
                    completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                )

            result_dict = self._read_result(result_file, stdout)
            return TaskResult(
                job_id=task.job_id,
                success=True,
                message=f"{task.flood_frequency}一遇 水沙耦合仿真完成",
                result=result_dict,
                completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            )

        except asyncio.TimeoutError:
            logger.error("水沙任务 %s 超时", task.job_id[:8])
            if proc and proc.returncode is None:
                try:
                    proc.kill()
                except Exception:
                    pass
            return TaskResult(
                job_id=task.job_id,
                success=False,
                message="水沙模型运行超时（超过 600 秒）",
                completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception as e:
            logger.error("水沙任务 %s 执行异常: %s", task.job_id[:8], str(e), exc_info=True)
            return TaskResult(
                job_id=task.job_id,
                success=False,
                message=f"水沙任务执行异常: {str(e)}",
                completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            )
        finally:
            try:
                if os.path.exists(result_file):
                    os.remove(result_file)
            except Exception:
                pass

    async def stop(self):
        """水沙模型无常驻进程，stop 为空操作"""
        logger.info("WaterSedimentExecutor 已关闭")

    # ─── 内部辅助 ────────────────────────────────────────

    def _read_result(self, result_file: str, stdout: bytes) -> dict | None:
        """读取模型结果 dict。

        优先从 result_file 读取（可靠）；若失败则尝试从 stdout 末行解析 JSON。
        """
        if os.path.exists(result_file):
            try:
                with open(result_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
            except Exception as e:
                logger.warning("读取 result_file 失败: %s", e)

        # 兜底：从 stdout 寻找最后一个 JSON 对象行
        text = stdout.decode("utf-8", errors="replace")
        for line in reversed(text.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    return data
            except Exception:
                continue
        return None

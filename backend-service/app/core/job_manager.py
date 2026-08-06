"""任务队列管理

JobManager 负责任务的生命周期管理：
- 任务提交（创建 → queued，返回 job_id）
- 任务执行（通过 executor 接口：queued → running → completed/failed）
- 状态查询
- 任务列表

JobManager 通过 BaseExecutor 接口执行任务，不直接依赖 MATLAB。
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Callable

from app.core.executor import BaseExecutor, TaskConfig, TaskResult


class JobRecord:
    """单个任务的状态记录"""

    def __init__(self, job_id: str, config: TaskConfig):
        self.job_id = job_id
        self.config = config
        self.status: str = "queued"  # queued | running | completed | failed
        self.progress_percent: float = 0.0
        self.created_at: str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.completed_at: str | None = None
        self.message: str | None = None
        self.result: TaskResult | None = None
        self.process_data: dict | None = None  # 最新过程数据
        self.evaluation_result: dict | None = None  # POST /evaluate 的计算结果缓存


class JobManager:
    """任务队列管理器

    使用 asyncio.Queue 串行化任务提交，
    后台 worker 通过 executor 接口执行任务。

    提供 current_job_id 属性，用于标记 MATLAB 回调所属的任务。
    """

    def __init__(self, executor: BaseExecutor):
        self._executor = executor
        self._jobs: dict[str, JobRecord] = {}
        self._queue: asyncio.Queue[JobRecord] = asyncio.Queue()
        self._running = False
        self._worker_task: asyncio.Task | None = None
        self._current_job_id: str | None = None  # 当前正在执行的任务 ID

    @property
    def current_job_id(self) -> str | None:
        """当前正在执行的任务 ID，供 /cb 端点标记回调归属"""
        return self._current_job_id

    async def start(self):
        """启动后台工作协程"""
        if self._running:
            return
        self._running = True
        self._worker_task = asyncio.create_task(self._worker_loop())

    async def stop(self):
        """停止后台工作协程"""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None

    async def submit_task(self, config: TaskConfig) -> JobRecord:
        """提交新任务

        返回 JobRecord（初始状态为 queued）。
        """
        job_id = str(uuid.uuid4())
        config.job_id = job_id
        record = JobRecord(job_id, config)
        self._jobs[job_id] = record
        await self._queue.put(record)
        return record

    def get_status(self, job_id: str) -> JobRecord | None:
        """查询任务状态，不存在返回 None"""
        return self._jobs.get(job_id)

    def list_jobs(self, status_filter: str | None = None) -> list[JobRecord]:
        """列出所有任务，可按状态过滤

        返回按创建时间倒序排列的列表。
        """
        records = list(self._jobs.values())
        if status_filter:
            records = [r for r in records if r.status == status_filter]
        records.sort(key=lambda r: r.created_at, reverse=True)
        return records

    async def _worker_loop(self):
        """后台工作循环：从队列取出任务，通过 executor 接口执行"""
        while self._running:
            try:
                record = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            try:
                # queued → running
                record.status = "running"
                record.message = "任务开始执行"
                self._current_job_id = record.job_id

                # 通过 executor 接口执行（Step 2 使用 MockExecutor）
                result = await self._executor.run(record.config)

                # running → completed
                record.status = "completed"
                record.message = result.message or "任务完成"
                record.progress_percent = 100.0
                record.completed_at = (
                    result.completed_at
                    or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                )
                record.result = result

            except asyncio.CancelledError:
                record.status = "failed"
                record.message = "任务被取消"
                # 不重新抛出，让 worker 继续处理后续任务
                # 但如果整体服务关闭，重新抛出给上层
                if not self._running:
                    raise

            except Exception as e:
                # running → failed
                record.status = "failed"
                record.message = str(e)
                record.completed_at = (
                    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                )

            finally:
                self._current_job_id = None
                self._queue.task_done()

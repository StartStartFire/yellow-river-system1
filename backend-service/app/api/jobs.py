"""任务相关端点

POST /run          — 提交优化任务
GET  /status/{id}  — 查询任务状态
GET  /jobs         — 列出所有任务
GET  /results/{id} — 获取优化结果
GET  /process/{id} — 补拉最新过程数据
"""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.job import RunRequest, JobStatusResponse, JobSummary
from app.schemas.result import ResultResponse
from app.core.executor import TaskConfig

logger = logging.getLogger(__name__)

router = APIRouter()

# 由 main.py lifespan 注入
_job_manager = None


def init(job_manager: "JobManager") -> None:
    """注入 JobManager 引用"""
    global _job_manager
    _job_manager = job_manager


@router.post("/run", response_model=JobStatusResponse)
async def run(req: RunRequest):
    """提交优化任务

    任务异步执行，返回 job_id 和初始状态。
    """
    if _job_manager is None:
        raise HTTPException(status_code=503, detail="服务未就绪")

    task_config = TaskConfig(
        algorithm=req.algorithm,
        pop=req.pop,
        iterate=req.iterate,
        M=req.M,
        Q_sediment=req.Q_sediment,
        K_mut=req.K_mut,
        crossover_rate=req.crossover_rate,
        flag_xixian=req.flag_xixian,
        year_start=req.year_start,
        year_end=req.year_end,
        initial_water_level_longyangxia=req.initial_water_level_longyangxia,
        initial_water_level_liujiaxia=req.initial_water_level_liujiaxia,
        ice_prevention_flows=req.ice_prevention_flows,
    )
    record = await _job_manager.submit_task(task_config)

    return JobStatusResponse(
        job_id=record.job_id,
        status=record.status,
        progress_percent=record.progress_percent,
        created_at=record.created_at,
        message=record.message,
    )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    """查询任务状态"""
    if _job_manager is None:
        raise HTTPException(status_code=503, detail="服务未就绪")

    record = _job_manager.get_status(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"任务 {job_id} 不存在")

    return JobStatusResponse(
        job_id=record.job_id,
        status=record.status,
        progress_percent=record.progress_percent,
        created_at=record.created_at,
        message=record.message,
    )


@router.get("/jobs", response_model=list[JobSummary])
async def list_jobs(status: str | None = None):
    """列出所有任务，可按状态过滤（queued/running/completed/failed）"""
    if _job_manager is None:
        raise HTTPException(status_code=503, detail="服务未就绪")

    records = _job_manager.list_jobs(status_filter=status)
    return [
        JobSummary(
            job_id=r.job_id,
            status=r.status,
            algorithm=r.config.algorithm,
            progress_percent=r.progress_percent,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/results/{job_id}", response_model=ResultResponse)
async def get_results(job_id: str):
    """获取优化结果

    返回 Pareto 解集矩阵（chromosome）和元数据。
    仅 completed 状态的任务有结果数据。
    """
    if _job_manager is None:
        raise HTTPException(status_code=503, detail="服务未就绪")

    record = _job_manager.get_status(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"任务 {job_id} 不存在")

    chromosome = None
    evaluating = None
    if record.result:
        if record.result.chromosome:
            chromosome = record.result.chromosome
        if record.result.evaluating is not None:
            evaluating = record.result.evaluating

    try:
        return ResultResponse(
            job_id=record.job_id,
            status=record.status,
            algorithm=record.config.algorithm,
            chromosome=chromosome,
            evaluating=evaluating,
            message=record.result.message if record.result else None,
            generated_at=record.completed_at,
        )
    except Exception as e:
        logger.error("构建 ResultResponse 失败: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"结果序列化失败: {str(e)}")


@router.get("/process/{job_id}")
async def get_process_data(job_id: str):
    """获取最新过程数据（水位/流量/出力曲线）

    当前端 WebSocket 连接较晚时，可通过此端点补拉最新过程数据。
    """
    if _job_manager is None:
        raise HTTPException(status_code=503, detail="服务未就绪")

    record = _job_manager.get_status(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"任务 {job_id} 不存在")

    return {
        "job_id": job_id,
        "status": record.status,
        "process_data": record.process_data,
        "message": None if record.process_data else "过程数据尚未生成",
    }


@router.get("/decision/{job_id}")
async def get_decision_plans(job_id: str):
    """获取决策分析方案明细（每个种群个体的过程曲线/目标满足度/水量分配）

    方案排序规则：
    - 已运行评价（ALL）：按序号总和整合排名排序，与评价分析页的"方案N"一致；
    - 未评价：按 Pareto rank + 拥挤距离排序。
    返回前 10 个方案。
    """
    if _job_manager is None:
        raise HTTPException(status_code=503, detail="服务未就绪")

    record = _job_manager.get_status(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"任务 {job_id} 不存在")
    if record.status != "completed":
        raise HTTPException(status_code=400, detail=f"任务尚未完成，当前状态: {record.status}")

    plans: list[dict] = []
    if record.result and record.result.plan_details:
        plans = list(record.result.plan_details)

    if not plans:
        return {
            "job_id": job_id,
            "status": record.status,
            "algorithm": record.config.algorithm,
            "evaluated": False,
            "year_start": record.config.year_start,
            "year_end": record.config.year_end,
            "plans": [],
            "message": "无决策方案明细数据（模型版本过旧，请重新运行任务）",
        }

    order = list(range(len(plans)))
    evaluated = False

    # 优先使用评价整合排名（与评价分析页方案编号一致）
    if record.evaluation_result:
        all_entry = next(
            (rk for rk in record.evaluation_result.get("rankings", [])
             if rk.get("algorithm") == "ALL" and rk.get("ranks")),
            None,
        )
        if all_entry:
            evaluated = True
            ranks = all_entry["ranks"]
            order.sort(key=lambda i: ranks[i] if i < len(ranks) else len(ranks) + i)
        elif record.result and record.result.chromosome:
            # 未评价时按 Pareto rank + 拥挤距离排序
            chrom = record.result.chromosome
            m_obj = record.config.M
            n_var = (len(chrom[0]) - m_obj - 2) if chrom and len(chrom[0]) > m_obj + 2 else 0

            def _pareto_key(i: int):
                row = chrom[i] if i < len(chrom) else []
                if n_var and len(row) == n_var + m_obj + 2 and row[n_var + m_obj] is not None:
                    rank_val = row[n_var + m_obj]
                    cd_val = row[n_var + m_obj + 1] or 0.0
                    return (rank_val, -cd_val, i)
                return (float("inf"), 0.0, i)

            order.sort(key=_pareto_key)

    labeled = []
    for pos, idx in enumerate(order[:10]):
        if idx >= len(plans):
            continue
        plan = dict(plans[idx])
        plan["index"] = idx + 1
        plan["label"] = f"方案{pos + 1}"
        labeled.append(plan)

    return {
        "job_id": job_id,
        "status": record.status,
        "algorithm": record.config.algorithm,
        "evaluated": evaluated,
        "year_start": record.config.year_start,
        "year_end": record.config.year_end,
        "plans": labeled,
        "message": None,
    }

"""评价系统路由

提供 POST /evaluate 和 GET /evaluate/{job_id} 端点，
调用 evaluation_system 对 Pareto 解集进行多算法排名。
"""
import logging
import os
import sys
from pathlib import Path
from typing import Any


from fastapi import APIRouter, HTTPException

from app.schemas.evaluate import EvaluateRequest, EvaluateResponse
from app.core.job_manager import JobManager

logger = logging.getLogger(__name__)

router = APIRouter()

# 由 main.py 在 startup 时注入
_job_manager: JobManager | None = None
_matlab_root: str = ""


def init(job_manager: JobManager, matlab_root: str) -> None:
    """由 main.py 在 lifespan startup 中调用，注入依赖"""
    global _job_manager, _matlab_root
    _job_manager = job_manager
    _matlab_root = matlab_root


# ─── 辅助函数 ────────────────────────────────────────────

def _build_evaluation_cache(result: dict, method: str,
                            algo_results: dict, integrated: dict) -> dict:
    """将 evaluation_system 返回的原始结果转为前端可用的缓存字典。

    为什么需要转换：evaluation_system 内部使用 numpy 数组，
    无法直接 JSON 序列化，需要在此统一转为 Python 原生 list。
    同时将散布在 3 个算法返回结果中的字段（排名/得分/收敛曲线/子系统分）
    按前端图表所需的结构重新聚合。
    """
    import numpy as np

    def _tolist(v: Any) -> list:
        if isinstance(v, np.ndarray):
            return v.tolist()
        return v if isinstance(v, list) else v

    cache: dict = {"method": method, "status": "success"}

    if method == "ALL":
        # ── 收敛曲线（NMF + PP 各 500 代） ──
        cache["convergence"] = {}
        for name in ("NMF", "PP"):
            ar = algo_results.get(name, {})
            res = ar.get("results", {})
            ch = res.get("cost_history", [])
            cache["convergence"][name] = _tolist(ch) if isinstance(ch, (list, np.ndarray)) else []

        # ── 排名表（NMF / PP / AHP_FUZZY + ALL 整合） ──
        cache["rankings"] = []
        all_rankings = integrated.get("all_rankings", {})
        for algo_name in ("NMF", "PP", "AHP_FUZZY"):
            ar = algo_results.get(algo_name, {})
            res = ar.get("results", {})
            ranks = _tolist(res.get("ranks", []))
            alg_rank = all_rankings.get(algo_name, ranks)
            # 根据算法类型取正确得分向量
            scores_map = {}
            if algo_name == "NMF":
                scores_map = res.get("H")
            elif algo_name == "PP":
                scores_map = res.get("z")
            elif algo_name == "AHP_FUZZY":
                scores_map = res.get("final_scores")
            scores_list = _tolist(scores_map) if scores_map is not None else None
            cache["rankings"].append({
                "algorithm": algo_name,
                "ranks": _tolist(alg_rank),
                "scores": scores_list,
                "execution_time": ar.get("execution_time", 0),
            })

        # ALL 整合排名（序号总和理论）
        final_ranks = _tolist(integrated.get("final_ranking", []))
        cache["rankings"].append({
            "algorithm": "ALL",
            "ranks": final_ranks,
            "scores": None,
            "execution_time": None,
        })

        # ── 算法得分雷达图（ALL 排名前 10 方案，按排名排序） ──
        # 各算法的 scores 数组索引与种群个体一一对应，ALL 的 ranks 给出整合排名
        all_entry = next((rk for rk in cache["rankings"] if rk["algorithm"] == "ALL"), None)
        # 按 ALL 整合排名升序排列索引（排名第 1 → 索引 0）
        if all_entry and all_entry["ranks"]:
            sorted_indices = sorted(
                range(len(all_entry["ranks"])),
                key=lambda i: all_entry["ranks"][i],
            )[:10]
        else:
            # 没有 ALL 排名时直接用 scores 长度
            sample = next((rk for rk in cache["rankings"] if rk["scores"]), None)
            sorted_indices = list(range(len(sample["scores"]) if sample else 0))[:10]

        # 构建雷达图 indicators（按算法，排除 ALL）
        non_all = [rk for rk in cache["rankings"] if rk["algorithm"] != "ALL"]
        radar_indicators = []
        for rk in non_all:
            scores_arr = rk["scores"] or []
            radar_indicators.append({
                "name": rk["algorithm"],
                "max": float(max(scores_arr)) if scores_arr else 1.0,
            })

        # 构建雷达图 plans（按排名排序，取前 10 个）
        plans = []
        for rank_pos, src_idx in enumerate(sorted_indices):
            vals = []
            for rk in non_all:
                scores_arr = rk["scores"] or []
                v = scores_arr[src_idx] if src_idx < len(scores_arr) else 0
                vals.append(float(v))
            plans.append({"plan": f"方案{rank_pos + 1}", "values": vals})

        cache["radar"] = {"indicators": radar_indicators, "plans": plans}

        # ── 个体 R1~R22 原始指标数据（前 10 名，按排名排序） ──
        # 从任意一个算法结果中取 original_data_matrix
        raw_matrix = None
        for ar in algo_results.values():
            res = ar.get("results", {})
            raw_matrix = res.get("original_data_matrix")
            if raw_matrix is not None:
                break
        if raw_matrix is not None:
            raw_matrix = _tolist(raw_matrix)
            # 子系统配置（与 unified_config.py 中 fuzzy.subsystem_config 一致）
            subsystems = [
                {"name": "水子系统", "indices": [0, 1, 2, 3, 4, 5]},
                {"name": "沙子系统", "indices": [6, 7]},
                {"name": "能子系统", "indices": [8, 9, 10, 11, 12]},
                {"name": "灾子系统", "indices": [13, 14, 15]},
                {"name": "生子系统", "indices": [16, 17, 18, 19, 20, 21]},
            ]
            # 取前 10 名个体的完整原始指标行
            schemes = []
            for rank_pos, src_idx in enumerate(sorted_indices):
                row = raw_matrix[src_idx] if src_idx < len(raw_matrix) else []
                schemes.append({"plan": f"方案{rank_pos + 1}", "values": [float(v) for v in row]})
            cache["raw_indicators"] = {
                "subsystems": subsystems,
                "schemes": schemes,
            }

    else:
        # 单算法模式
        results_data = result.get("results", {})
        ranks = _tolist(results_data.get("ranks", []))

        ch = results_data.get("cost_history", [])
        if ch is not None and len(ch) > 0:
            cache["convergence"] = {method: _tolist(ch)}

        scores_arr = None
        if method == "NMF":
            scores_arr = results_data.get("H")
        elif method == "PP":
            scores_arr = results_data.get("z")
        elif method == "AHP_FUZZY":
            scores_arr = results_data.get("final_scores")

        cache["rankings"] = [{
            "algorithm": method,
            "ranks": ranks,
            "scores": _tolist(scores_arr) if scores_arr is not None else None,
            "execution_time": result.get("execution_time", 0),
        }]

        # ── 单算法雷达图（取该算法排名前 10 方案的分项得分） ──
        single_rk = cache["rankings"][0]
        scores_arr = single_rk.get("scores") or []
        n = len(scores_arr)
        top_n = min(10, n)

        # 按算法自身排名取前 10
        ranks_arr = single_rk.get("ranks") or []
        if ranks_arr and len(ranks_arr) >= n:
            sorted_idx = sorted(range(n), key=lambda i: ranks_arr[i])[:top_n]
        else:
            sorted_idx = list(range(top_n))

        radar_indicators = [{"name": method, "max": float(max(scores_arr)) if scores_arr else 1.0}]
        plans = []
        for rank_pos, src_idx in enumerate(sorted_idx):
            v = float(scores_arr[src_idx]) if src_idx < n else 0
            plans.append({
                "plan": f"方案{rank_pos + 1}",
                "values": [v],
            })
        cache["radar"] = {"indicators": radar_indicators, "plans": plans}

    return cache


# ─── 端点 ────────────────────────────────────────────────

@router.post("", response_model=EvaluateResponse)
async def evaluate_job(req: EvaluateRequest):
    """对已完成任务进行评价排名

    支持 NMF / PP / AHP_FUZZY / ALL 四种方法。
    结果缓存于 JobRecord.evaluation_result。
    """
    if _job_manager is None:
        raise HTTPException(status_code=503, detail="服务未就绪")

    record = _job_manager.get_status(req.job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"任务 {req.job_id} 不存在")
    if record.status != "completed":
        raise HTTPException(status_code=400, detail=f"任务尚未完成，当前状态: {record.status}")
    if not record.result or not record.result.evaluating:
        raise HTTPException(status_code=400, detail="任务结果中无 evaluating 评价指标矩阵")

    eval_sys_dir = str(Path(_matlab_root).parent / "evaluation-model")
    if eval_sys_dir not in sys.path:
        sys.path.insert(0, eval_sys_dir)

    try:
        import matplotlib
        matplotlib.use('Agg')

        import numpy as np
        from evaluation_system import run_single_algorithm, run_complete_evaluation

        silent_config = {
            'output': {
                'save_plots': False, 'save_convergence_plot': False,
                'save_data_files': False, 'save_scheme_matrix': False,
                'save_decision_params': False, 'save_rankings': False,
                'save_matrix_outputs': False, 'save_pairwise_rankings': False,
            },
        }

        data_matrix = np.array(record.result.evaluating, dtype=float)
        logger.info("开始评价: job_id=%s, method=%s, shape=%s",
                     req.job_id[:8], req.method, data_matrix.shape)

        if req.method == "ALL":
            result = run_complete_evaluation(data_source=data_matrix, config_dict=silent_config)
            if not result.get("success"):
                return EvaluateResponse(job_id=req.job_id, method=req.method,
                                        status="error", message=result.get("error", "评价失败"))

            algo_results = result.get("algorithm_results", {})
            integrated = result.get("integrated_results", {})
            cache = _build_evaluation_cache(result, req.method, algo_results, integrated)
            record.evaluation_result = cache

            final_ranking = integrated.get("final_ranking")
            ranking_list = final_ranking.tolist() if final_ranking is not None else None
            return EvaluateResponse(job_id=req.job_id, method=req.method,
                                    status="success", ranking=ranking_list, details=cache)

        else:
            result = run_single_algorithm(req.method, data_source=data_matrix, config_dict=silent_config)
            if not result.get("success"):
                return EvaluateResponse(job_id=req.job_id, method=req.method,
                                        status="error", message=result.get("error", "评价失败"))

            cache = _build_evaluation_cache(result, req.method, {}, {})
            record.evaluation_result = cache

            results_data = result.get("results", {})
            ranks = results_data.get("ranks")
            scores_arr = None
            if req.method == "NMF":
                scores_arr = results_data.get("H")
            elif req.method == "PP":
                scores_arr = results_data.get("z")
            elif req.method == "AHP_FUZZY":
                scores_arr = results_data.get("final_scores")

            ranking_list = ranks.tolist() if ranks is not None else None
            scores_list = scores_arr.tolist() if scores_arr is not None else None
            best_idx = int(results_data["best_scheme_index"]) if results_data.get("best_scheme_index") is not None else None

            return EvaluateResponse(job_id=req.job_id, method=req.method, status="success",
                                    ranking=ranking_list, scores=scores_list,
                                    best_scheme_index=best_idx, details=cache)

    except ImportError as e:
        logger.error("导入 evaluation_system 失败: %s", e)
        raise HTTPException(status_code=500, detail=f"评价系统模块导入失败: {e}")
    except Exception as e:
        logger.error("评价失败: %s", e, exc_info=True)
        return EvaluateResponse(job_id=req.job_id, method=req.method,
                                status="error", message=f"评价过程出错: {e}")


@router.get("/{job_id}")
async def get_evaluation_result(job_id: str):
    """获取已缓存的评价结果"""
    if _job_manager is None:
        raise HTTPException(status_code=503, detail="服务未就绪")

    record = _job_manager.get_status(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"任务 {job_id} 不存在")

    if record.evaluation_result is None:
        return {"job_id": job_id, "status": "not_evaluated", "message": "尚未进行评价"}

    result = dict(record.evaluation_result)
    result["job_id"] = job_id
    result["status"] = "evaluated"  # 覆盖缓存内部的 "success"，统一用 "evaluated"
    return result

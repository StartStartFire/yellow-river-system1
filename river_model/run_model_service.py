# -*- coding: utf-8 -*-
"""
run_model_service.py — 水沙耦合模型 子进程服务入口

由后端（FastAPI）以子进程方式调用：
    python run_model_service.py --flood_frequency 2年 --job_id <id> [--cb_url http://127.0.0.1:18080/cb]

功能：
1. 设置环境变量（RIVER_FLOOD_FREQ / RIVER_CB_URL / RIVER_JOB_ID）并 import coupledModel，
   触发完整水沙耦合模型运行（调度→反馈演进→冲淤）；
2. coupledModel 在反馈迭代中通过 _cb_push 向 /cb 实时推送 progress/process_data；
3. 运行结束后，读取 coupledModel 的全局结果，并用拆分模块 mod_sediment 计算冲淤，
   将结构化的最终结果以 JSON 写入 stdout，供后端解析。

说明：coupledModel 以 matplotlib 无头模式运行，plt.show() 被屏蔽；结果经 stdout JSON 回传。
"""
import os
import sys
import json
import argparse

# ---------- 环境准备 ----------
# 无头 matplotlib（必须在 pyplot 导入前设置）
import matplotlib
matplotlib.use("Agg")

RIVER_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RIVER_DIR)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--flood_frequency", default="2年")
    p.add_argument("--job_id", default="")
    p.add_argument("--cb_url", default="")
    p.add_argument("--number", type=int, default=20)
    p.add_argument("--result_file", default="")
    return p.parse_args()


def _flat(a):
    import numpy as np
    return [float(v) for v in np.asarray(a, dtype=float).flatten()]


def _push(cb_url, data_type, data):
    if not cb_url:
        return
    import urllib.request
    try:
        req = urllib.request.Request(
            cb_url,
            data=json.dumps({"type": data_type, "data": data}).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass


def main():
    args = _parse_args()

    # 设置环境变量供 coupledModel 回调与非交互读取
    os.environ["RIVER_FLOOD_FREQ"] = args.flood_frequency
    os.environ["RIVER_CB_URL"] = args.cb_url
    os.environ["RIVER_JOB_ID"] = args.job_id
    os.environ["RIVER_Z_INI"] = "默认值"  # 服务模式：不使用交互输入初始水位，用默认值

    # 切换工作目录到模型目录（数据均为相对路径）
    os.chdir(RIVER_DIR)

    import matplotlib.pyplot as plt
    plt.show = lambda *a, **k: None  # 屏蔽 GUI

    # 运行整个模型（顶层脚本在 import 时执行，含回调推送）
    import coupledModel as cm

    # ---------- 收集结构化结果 ----------
    def get(name, default=None):
        return getattr(cm, name, default)

    # ---------- M2 洪水演进：调用拆分模块 mod_routing ----------
    # 输入：M1 收敛后的刘家峡下泄（Q_out_LJX） + 民和/享堂支流来水。
    # 说明：coupledModel 内部在收敛后也执行这一步（其行 1913-1934）；
    #       此处改用拆分模块 run_routing 产出 8 断面结果，并与其做一致性校验。
    from mod_routing import run_routing

    sections_names = ["兰州", "下河沿", "青铜峡", "石嘴山",
                      "巴彦高勒", "三湖河口", "包头", "头道拐"]
    orig_attr = {
        "兰州": "simulated_lanzhou", "下河沿": "simulated_xiaheyan",
        "青铜峡": "simulated_qingtongxia", "石嘴山": "simulated_shizuishan",
        "巴彦高勒": "simulated_bayangaole", "三湖河口": "simulated_sanhuhekou",
        "包头": "simulated_baotou", "头道拐": "simulated_toudaoguai",
    }

    ljx_outflow = _flat(get("Q_out_LJX", []))
    mh_flow = list(get("mh_flow", []) or [])
    xt_flow = list(get("xt_flow", []) or [])
    routing_sections = run_routing(ljx_outflow, mh_flow, xt_flow)

    # 用拆分模块输出作为断面结果，同时与耦合模型内部演进结果对比，验证等价性
    sections = {}
    m2_max_diff = 0.0
    for nm in sections_names:
        routed = [float(v) for v in routing_sections.get(nm, [])]
        original = _flat(get(orig_attr[nm], []))
        sections[nm] = routed
        for a, b in zip(routed, original):
            d = abs(a - b)
            if d > m2_max_diff:
                m2_max_diff = d

    iteration_hist = {
        "liujiaxia": [_flat(x) for x in (get("LJX_discharge_history", []) or [])],
        "lanzhou": [_flat(x) for x in (get("simulated_lanzhou_history", []) or [])],
    }

    # ---------- M1 水沙调度：调用服务化适配器 mod_scheduling ----------
    # M1 状态耦合强，无法纯函数式拆分，采用适配器模式统一接口并抽取调度结果
    from mod_scheduling import extract_scheduling
    scheduling = extract_scheduling(cm)

    result = {
        "flood_frequency": get("flood_frequency", args.flood_frequency),
        "iteration_count": len(get("simulated_lanzhou_history", []) or []),
        "liujiaxia_outflow": _flat(get("Q_out_LJX", [])),
        "sections": sections,
        "iteration_history": iteration_hist,
        "m2_consistency_max_diff": m2_max_diff,
        # 保持向后兼容：前端使用 reservoir.longyangxia
        "reservoir": {"longyangxia": scheduling["reservoirs"]["龙羊峡"]},
        # M1 服务化输出：6 库完整调度过程（新版接口）
        "scheduling": scheduling["reservoirs"],
    }

    # ---------- 冲淤（复用拆分模块 M3） ----------
    from mod_sediment import run_sediment
    try:
        sed = run_sediment(sections.get("包头", []), sections.get("头道拐", []),
                           label=get("flood_frequency", args.flood_frequency), quiet=True)
        result["sediment"] = sed
    except Exception as e:
        result["sediment"] = {"error": str(e)}

    # ---------- 最终过程数据回传 ----------
    if args.cb_url:
        fb = args.flood_frequency
        _push(args.cb_url, "progress",
              {"job_id": args.job_id, "iteration": result["iteration_count"],
               "progress_percent": 100.0, "message": f"{fb}一遇耦合计算完成"})
        _push(args.cb_url, "process_data",
              {"job_id": args.job_id, "iteration": result["iteration_count"],
               "flood_frequency": result["flood_frequency"],
               "message": f"{fb}一遇耦合反馈实时凑峰调度结果",
               "liujiaxia_outflow": result["liujiaxia_outflow"],
               "sections": sections,
               "iteration_history": iteration_hist,
               "reservoir": result.get("reservoir"),
               "sediment": result.get("sediment")})

    # ---------- 结果写 stdout ----------
    text = json.dumps(result, ensure_ascii=False)
    print(text)
    if args.result_file:
        with open(args.result_file, "w", encoding="utf-8") as f:
            f.write(text)
        if not args.job_id:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

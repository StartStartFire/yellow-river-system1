# -*- coding: utf-8 -*-
"""mod_scheduling.py — M1 水沙调度 服务化适配器（Adapter）

背景（对应论文“拆分准则”的边界）：
    M1（coupledModel.run_real_time_scheduling）与数据加载、全局变量、
    自迭代耦合逻辑深度绑定，**状态耦合强**，无法像 M2/M3 那样做纯函数式拆分。
    因此本模块以**适配器（Adapter）模式**，在完整模型计算结果之上提供
    统一、稳定的调度结果接口。

与 M2/M3 的对比：
    - M2 洪水演进 / M3 输沙造床：纯函数、可独立拆分、可单独调用、可单元验证；
    - M1 水沙调度：状态耦合强 → 采用适配器封装（接口统一，但依赖完整运行结果）。

接口：
    extract_scheduling(cm_module) -> dict     # 从已运行的 coupledModel 抽取（适配器核心）
    run_scheduling(flood_frequency) -> dict   # 便捷入口：触发完整模型运行后抽取
"""

import os
import sys

# 6 个梯级水库：中文名 → coupledModel 全局变量后缀
RESERVOIRS = [
    ("龙羊峡", "LYX"),
    ("拉西瓦", "LXW"),
    ("李家峡", "LJ"),
    ("公伯峡", "GBX"),
    ("积石峡", "JSX"),
    ("刘家峡", "LJX"),
]

# 统一字段 → coupledModel 全局变量前缀
_VARS = {
    "level": "Zup",              # 水位过程
    "power": "N",                # 出力过程
    "inflow": "Q_in",            # 入库流量过程
    "outflow": "Q_out",          # 出库/下泄流量过程
    "abandoned": "Q_ele_abandoned",  # 弃水过程
}


def _flat(a):
    """转为一维 Python float 列表。"""
    import numpy as np
    return [float(v) for v in np.asarray(a, dtype=float).flatten()]


def extract_scheduling(cm_module) -> dict:
    """适配器核心：从已运行的 coupledModel 模块抽取调度结果。

    参数:
        cm_module: 已 import 并执行完毕的 coupledModel 模块对象

    返回:
        {
          "reservoirs": {
             "龙羊峡": {"level":[...], "power":[...], "inflow":[...],
                        "outflow":[...], "abandoned":[...]},
             ... 6 库 ...
          },
          "liujiaxia_outflow": [...]   # 刘家峡下泄（供 M2 演进使用）
        }
    """
    reservoirs = {}
    for name, code in RESERVOIRS:
        entry = {}
        for key, prefix in _VARS.items():
            entry[key] = _flat(getattr(cm_module, f"{prefix}_{code}", []))
        reservoirs[name] = entry
    return {
        "reservoirs": reservoirs,
        "liujiaxia_outflow": _flat(getattr(cm_module, "Q_out_LJX", [])),
    }


def run_scheduling(flood_frequency: str = "2年") -> dict:
    """便捷入口：运行完整模型后抽取调度结果。

    注意：M1 状态耦合强，无法脱离完整模型单独计算，本函数会触发一次完整
    coupledModel 运行（约 160 秒）。这也正是 M1 与 M2/M3 的差异所在。
    """
    river_dir = os.path.dirname(os.path.abspath(__file__))
    if river_dir not in sys.path:
        sys.path.insert(0, river_dir)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    os.environ["RIVER_FLOOD_FREQ"] = flood_frequency
    os.environ.setdefault("RIVER_CB_URL", "")
    os.environ.setdefault("RIVER_JOB_ID", "scheduling")
    os.environ.setdefault("RIVER_Z_INI", "默认值")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.show = lambda *a, **k: None  # noqa: E731

    import coupledModel as cm
    return extract_scheduling(cm)

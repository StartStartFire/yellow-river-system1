# -*- coding: utf-8 -*-
"""生成 M2 洪水演进模块（mod_routing）的参考数据 fixture。

运行一次完整耦合模型，保存：
  - 输入：刘家峡下泄（Q_out_LJX）、民和/享堂支流来水
  - 输出：8 个断面模拟流量（coupledModel 内部演进结果）
供 test_mod_routing.py 做“模块独立调用 + 数值等价”校验。

用法：
    python tests/make_m2_fixture.py [重现期，默认 2年]
"""
import os
import sys
import json

RIVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RIVER_DIR)
os.chdir(RIVER_DIR)

# 控制台编码（模型内部有中文 print，Windows GBK 控制台会报错）
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 无头 matplotlib（在 import coupledModel 前设置）
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.show = lambda *a, **k: None  # noqa: E731

freq = sys.argv[1] if len(sys.argv) > 1 else "2年"
os.environ["RIVER_FLOOD_FREQ"] = freq
os.environ["RIVER_CB_URL"] = ""      # 关闭回调，纯计算
os.environ["RIVER_JOB_ID"] = "fixture"
os.environ["RIVER_Z_INI"] = "默认值"

import numpy as np  # noqa: E402
import coupledModel as cm  # noqa: E402  (import 即执行完整模型)


def flat(a):
    return [float(v) for v in np.asarray(a, dtype=float).flatten()]


SECTIONS = ["兰州", "下河沿", "青铜峡", "石嘴山", "巴彦高勒", "三湖河口", "包头", "头道拐"]
ATTRS = ["simulated_lanzhou", "simulated_xiaheyan", "simulated_qingtongxia",
         "simulated_shizuishan", "simulated_bayangaole", "simulated_sanhuhekou",
         "simulated_baotou", "simulated_toudaoguai"]

fixture = {
    "flood_frequency": freq,
    "inputs": {
        "liujiaxia_outflow": flat(cm.Q_out_LJX),
        "mh_flow": [float(v) for v in cm.mh_flow],
        "xt_flow": [float(v) for v in cm.xt_flow],
    },
    "expected_sections": {
        nm: flat(getattr(cm, ATTRS[i])) for i, nm in enumerate(SECTIONS)
    },
}

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"m2_reference_{freq}.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(fixture, f, ensure_ascii=False)
print("fixture written:", out)

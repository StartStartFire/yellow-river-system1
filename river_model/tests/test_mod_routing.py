# -*- coding: utf-8 -*-
"""M2 洪水演进模块（mod_routing）单元测试 / 独立性验证。

目的（论文实验证据）：
  1. 结构完整性：8 断面齐全、长度一致
  2. 确定性：相同输入 → 相同输出
  3. 物理正确性：支流汇入使兰州断面流量增大
  4. 数值正确性：与马斯京根递推公式逐点一致
  5. 独立性 + 等价性：仅调用 mod_routing（不经过 coupledModel），
     即复现完整模型的 8 断面结果（最大偏差 < 1e-9）

运行：
    python tests/test_mod_routing.py
（可选）先生成参考数据：python tests/make_m2_fixture.py
"""
import glob
import json
import os
import sys
import time

RIVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RIVER_DIR)

import numpy as np  # noqa: E402
from mod_routing import (  # noqa: E402
    run_routing,
    muskingum_nonlinear_lanzhou,
    calculate_nonlinear_coefficients,
    DEFAULT_PARAMS,
    SECTION_ORDER,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def _maxdiff(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


def test_structure_and_determinism():
    q = [1000.0] * 5 + [5000.0, 6000.0, 5500.0] + [2000.0] * 5 + [1000.0] * 7
    out1 = run_routing(q)
    out2 = run_routing(q)
    assert set(out1.keys()) == set(SECTION_ORDER), f"断面集合不符: {list(out1.keys())}"
    for nm in SECTION_ORDER:
        assert len(out1[nm]) == len(q), f"{nm} 长度不符"
        assert _maxdiff(out1[nm], out2[nm]) == 0.0, f"{nm} 非确定性"
    print("[PASS] 1. 结构完整（8 断面、长度一致） + 确定性")


def test_tributary_effect():
    q = [1000.0] * 20
    base = run_routing(q)
    with_trib = run_routing(q, mh_flow=[200.0] * 20, xt_flow=[100.0] * 20)
    # 支流汇入应使兰州断面流量增大
    assert with_trib["兰州"][5] > base["兰州"][5], "支流汇入未生效"
    print("[PASS] 2. 物理正确性（支流来水使兰州断面流量增大）")


def test_recursion_correctness():
    """手工复现兰州段马斯京根递推，验证与模块实现逐点一致。"""
    q = np.array([1000., 1200., 1500., 1300., 1100., 900.] + [800.] * 14)
    mh = np.zeros(20)
    xt = np.zeros(20)
    got = muskingum_nonlinear_lanzhou(DEFAULT_PARAMS["lanzhou"], q, mh, xt)

    k, x, a, b, c = DEFAULT_PARAMS["lanzhou"]
    s1 = np.zeros(20)
    s1[0] = q[0]
    for i in range(1, 20):
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, q[i], q.max(), a, b, c)
        s1[i] = c0 * q[i] + c1 * q[i - 1] + c2 * s1[i - 1]
    manual = (s1 + mh + xt) * (1 + 0.05)

    assert _maxdiff(got.tolist(), manual.tolist()) < 1e-12, "递推公式不一致"
    print("[PASS] 3. 数值正确性（马斯京根递推逐点一致）")


def test_reference_equivalence():
    """仅用拆分模块复现完整模型的 8 断面结果。"""
    files = sorted(glob.glob(os.path.join(HERE, "m2_reference_*.json")))
    if not files:
        print("[SKIP] 4. 未找到参考数据（请先运行 tests/make_m2_fixture.py）")
        return
    ref = json.load(open(files[-1], encoding="utf-8"))
    inp = ref["inputs"]

    t0 = time.perf_counter()
    out = run_routing(inp["liujiaxia_outflow"], inp["mh_flow"], inp["xt_flow"])
    elapsed_ms = (time.perf_counter() - t0) * 1000

    maxdiff = 0.0
    for nm, expected in ref["expected_sections"].items():
        maxdiff = max(maxdiff, _maxdiff(out[nm], expected))

    assert maxdiff < 1e-9, f"与完整模型结果偏差过大: {maxdiff}"
    print(f"[PASS] 4. 独立性+等价性（重现期 {ref['flood_frequency']}，"
          f"最大偏差 {maxdiff:.2e}，M2 独立运行 {elapsed_ms:.1f} ms）")


if __name__ == "__main__":
    test_structure_and_determinism()
    test_tributary_effect()
    test_recursion_correctness()
    test_reference_equivalence()
    print("\nM2 洪水演进模块验证全部通过。")

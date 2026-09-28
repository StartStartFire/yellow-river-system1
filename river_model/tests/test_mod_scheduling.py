# -*- coding: utf-8 -*-
"""M1 水沙调度 服务化适配器（mod_scheduling）测试。

M1 状态耦合强，无法脱离完整耦合模型单独计算（这正是与 M2/M3 的差异）。
本测试用**伪模块**验证适配器的接口映射与容错；真实抽取结果由
run_model_service.py 端到端运行验证。

运行：
    python tests/test_mod_scheduling.py
"""
import os
import sys

RIVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RIVER_DIR)

from mod_scheduling import extract_scheduling, RESERVOIRS, _VARS  # noqa: E402


def _make_fake_cm():
    class FakeCM:
        pass
    for _, code in RESERVOIRS:
        for key, prefix in _VARS.items():
            setattr(FakeCM, f"{prefix}_{code}", [1.0, 2.0, 3.0])
    FakeCM.Q_out_LJX = [10.0, 20.0, 30.0]
    return FakeCM


def test_structure():
    out = extract_scheduling(_make_fake_cm())
    assert set(out.keys()) == {"reservoirs", "liujiaxia_outflow"}
    assert len(out["reservoirs"]) == 6, "应为 6 个梯级水库"
    for name, _ in RESERVOIRS:
        assert name in out["reservoirs"], f"缺少水库 {name}"
        entry = out["reservoirs"][name]
        assert set(entry.keys()) == set(_VARS.keys()), f"{name} 字段不全"
        for k in _VARS:
            assert isinstance(entry[k], list) and len(entry[k]) == 3
    assert out["liujiaxia_outflow"] == [10.0, 20.0, 30.0]
    print("[PASS] M1 适配器结构：6 库 × 5 变量（水位/出力/入库/出库/弃水）+ 刘家峡下泄")


def test_missing_graceful():
    class Empty:
        pass
    out = extract_scheduling(Empty)
    assert len(out["reservoirs"]) == 6
    assert out["liujiaxia_outflow"] == []
    print("[PASS] M1 适配器容错：字段缺失时返回空列表（不抛异常）")


if __name__ == "__main__":
    test_structure()
    test_missing_graceful()
    print("\nM1 水沙调度适配器验证通过。")

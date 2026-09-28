# -*- coding: utf-8 -*-
"""
mod_routing.py — 洪水演进子模型（水文水动力 / 非线性马斯京根法）

模型拆分模块 M2：承接"水沙调度"子模型输出的刘家峡下泄过程，
叠加区间支流来水，沿黄河上游 8 个断面逐段演进，得到各断面洪水过程。

来源：coupledModel.py（西安理工大学 水沙统一调度 + 水文水动力演变 + 输沙造床耦合模型）
本模块仅复制其"洪水演进"纯函数，未改动任何计算逻辑。

接口：run_routing(liujiaxia_outflow, mh_flow=None, xt_flow=None, params=None) -> dict

返回 dict 的键（8 断面，自上游至下游）：
    兰州、下河沿、青铜峡、石嘴山、巴彦高勒、三湖河口、包头、头道拐
"""

import numpy as np


# ---------- 演进参数（与 coupledModel.py 行 1404-1433 完全一致） ----------
DEFAULT_PARAMS = {
    "lanzhou":     [0.9974, 0.1593, 0.0586, 0.1295, 0.7299],
    "xiaheyan":    [1.0617, 0.3496, 0.0538, 0.1072, 0.147],
    "qingtongxia": [1.3369, 0.4798, 0.0228, 0.3047, 0.6955],
    "shizuishan":  [1.2781, 0.2277, 0.1569, 0.0002, 0.5459],
    "bayangaole":  [1.7758, 0.2075, 0.0802, 0.0789, -0.0946],
    "sanhuhekou":  [1.0937, 0.5155, 0.0244, 0.2699, 0.4313],
    "baotou":      [1.1383, 0.3418, 0.1114, 0.0515, 0.0623],
    "toudaoguai":  [0.8599, 0.4563, 0.0492, 0.1876, 0.3661],
}

# 断面顺序（自上游至下游）
SECTION_ORDER = ["兰州", "下河沿", "青铜峡", "石嘴山", "巴彦高勒", "三湖河口", "包头", "头道拐"]


# ---------- 核心纯函数（与 coupledModel.py 相同） ----------
def calculate_nonlinear_coefficients(k, x, flow, max_flow, a, b, c):
    """计算非线性马斯京根系数（c0, c1, c2），含数值稳定性处理。"""
    if max_flow == 0:
        max_flow = 1e-6
    if flow > max_flow:
        flow = max_flow
    if flow < 0:
        flow = 0

    time_varying_index = a + b * np.exp(-c * flow / max_flow)
    denominator = (1 + 0.5 * x * k) ** 2
    nonlinear_factor = np.power(flow, time_varying_index)

    if denominator == 0:
        denominator = 1e-6

    c0 = 0.5 * (1 - x / k) * nonlinear_factor / denominator
    c1 = (0.5 * (1 - x / k) * nonlinear_factor - k) / denominator
    c2 = 1 - c0 - c1

    c0 = np.clip(c0, 0, 1)
    c1 = np.clip(c1, 0, 1)
    c2 = np.clip(c2, 0, 1)

    return c0, c1, c2


def muskingum_nonlinear_lanzhou(params, liujiaxiastream_data, mh_flow, xt_flow):
    """兰州段：刘家峡下泄 → 兰州，叠加民和/享堂支流。"""
    k, x, a, b, c = params
    simulated_stream1 = np.zeros_like(liujiaxiastream_data)
    simulated_stream = np.zeros_like(liujiaxiastream_data)
    max_flow = np.max(liujiaxiastream_data)
    simulated_stream1[0] = liujiaxiastream_data[0]

    for i in range(1, len(liujiaxiastream_data)):
        previous_flow = simulated_stream1[i - 1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, liujiaxiastream_data[i], max_flow, a, b, c)
        simulated_stream1[i] = c0 * liujiaxiastream_data[i] + c1 * liujiaxiastream_data[i - 1] + c2 * previous_flow

    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = (simulated_stream1[i] + mh_flow[i] + xt_flow[i]) * (1 + 0.05)

    return simulated_stream


def muskingum_nonlinear_xiaheyan(params, lanzhoustream_data):
    """下河沿段：兰州 → 下河沿（考虑靖远支流 -4%）。"""
    k, x, a, b, c = params
    simulated_stream1 = np.zeros_like(lanzhoustream_data)
    simulated_stream = np.zeros_like(lanzhoustream_data)
    bankfull_flow = 4000
    simulated_stream1[0] = lanzhoustream_data[0]

    for i in range(1, len(lanzhoustream_data)):
        previous_flow = simulated_stream1[i - 1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, lanzhoustream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * lanzhoustream_data[i] + c1 * lanzhoustream_data[i - 1] + c2 * previous_flow

    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 - 0.04)

    return simulated_stream


def muskingum_nonlinear_qingtongxia(params, xiaheyanstream_data):
    """青铜峡段：下河沿 → 青铜峡（考虑泉眼山支流 -20%）。"""
    k, x, a, b, c = params
    simulated_stream1 = np.zeros_like(xiaheyanstream_data)
    simulated_stream = np.zeros_like(xiaheyanstream_data)
    bankfull_flow = 3000
    simulated_stream1[0] = xiaheyanstream_data[0]

    for i in range(1, len(xiaheyanstream_data)):
        previous_flow = simulated_stream1[i - 1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, xiaheyanstream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * xiaheyanstream_data[i] + \
                              c1 * xiaheyanstream_data[i - 1] + \
                              c2 * previous_flow

    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 - 0.2)

    return simulated_stream


def muskingum_nonlinear_shizuishan(params, qingtongxia_data):
    """石嘴山段：青铜峡 → 石嘴山。"""
    k, x, a, b, c = params
    simulated_stream1 = np.zeros_like(qingtongxia_data)
    simulated_stream = np.zeros_like(qingtongxia_data)
    bankfull_flow = 2300
    simulated_stream1[0] = qingtongxia_data[0]

    for i in range(1, len(qingtongxia_data)):
        previous_flow = simulated_stream1[i - 1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, qingtongxia_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * qingtongxia_data[i] + \
                              c1 * qingtongxia_data[i - 1] + \
                              c2 * previous_flow

    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 + 0.08)

    return simulated_stream


def muskingum_nonlinear_bayangaole(params, shizuishanstream_data):
    """巴彦高勒段：石嘴山 → 巴彦高勒。"""
    k, x, a, b, c = params
    simulated_stream1 = np.zeros_like(shizuishanstream_data)
    simulated_stream = np.zeros_like(shizuishanstream_data)
    bankfull_flow = 2300
    simulated_stream1[0] = shizuishanstream_data[0]

    for i in range(1, len(shizuishanstream_data)):
        previous_flow = simulated_stream1[i - 1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, shizuishanstream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * shizuishanstream_data[i] + \
                              c1 * shizuishanstream_data[i - 1] + \
                              c2 * previous_flow

    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 - 0.15)

    return simulated_stream


def muskingum_nonlinear_sanhuhekou(params, bayangaolestream_data):
    """三湖河口段：巴彦高勒 → 三湖河口。"""
    k, x, a, b, c = params
    simulated_stream1 = np.zeros_like(bayangaolestream_data)
    simulated_stream = np.zeros_like(bayangaolestream_data)
    bankfull_flow = 2300
    simulated_stream1[0] = bayangaolestream_data[0]

    for i in range(1, len(bayangaolestream_data)):
        previous_flow = simulated_stream1[i - 1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, bayangaolestream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * bayangaolestream_data[i] + \
                              c1 * bayangaolestream_data[i - 1] + \
                              c2 * previous_flow

    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 + 0.03)

    return simulated_stream


def muskingum_nonlinear_baotou(params, sanhuhekoustream_data):
    """包头段：三湖河口 → 包头。"""
    k, x, a, b, c = params
    simulated_stream1 = np.zeros_like(sanhuhekoustream_data)
    simulated_stream = np.zeros_like(sanhuhekoustream_data)
    bankfull_flow = 2300
    simulated_stream1[0] = sanhuhekoustream_data[0]

    for i in range(1, len(sanhuhekoustream_data)):
        previous_flow = simulated_stream1[i - 1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, sanhuhekoustream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * sanhuhekoustream_data[i] + \
                              c1 * sanhuhekoustream_data[i - 1] + \
                              c2 * previous_flow

    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 - 0.02)

    return simulated_stream


def muskingum_nonlinear_toudaoguai(params, baotoustream_data):
    """头道拐段：包头 → 头道拐。"""
    k, x, a, b, c = params
    simulated_stream1 = np.zeros_like(baotoustream_data)
    simulated_stream = np.zeros_like(baotoustream_data)
    bankfull_flow = 2300
    simulated_stream1[0] = baotoustream_data[0]

    for i in range(1, len(baotoustream_data)):
        previous_flow = simulated_stream1[i - 1]
        c0, c1, c2 = calculate_nonlinear_coefficients(k, x, baotoustream_data[i], bankfull_flow, a, b, c)
        simulated_stream1[i] = c0 * baotoustream_data[i] + \
                              c1 * baotoustream_data[i - 1] + \
                              c2 * previous_flow

    for i in range(0, len(simulated_stream)):
        simulated_stream[i] = simulated_stream1[i] * (1 - 0.02)

    return simulated_stream


# ---------- 对外统一接口 ----------
def run_routing(liujiaxia_outflow, mh_flow=None, xt_flow=None, params=None):
    """洪水演进子模型统一入口。

    参数:
        liujiaxia_outflow: 刘家峡下泄过程（array-like）
        mh_flow:           民和支流来水（可选，缺省为 0）
        xt_flow:           享堂支流来水（可选，缺省为 0）
        params:            各河段演进参数覆盖（可选，键为断面拼音名）

    返回:
        dict: { 断面名: list }，覆盖 8 个断面自上游至下游
    """
    upstream = np.asarray(liujiaxia_outflow, dtype=float)
    n = len(upstream)
    mh = np.zeros(n, dtype=float) if mh_flow is None else np.asarray(mh_flow, dtype=float)
    xt = np.zeros(n, dtype=float) if xt_flow is None else np.asarray(xt_flow, dtype=float)

    p = dict(DEFAULT_PARAMS)
    if params:
        p.update(params)

    lanzhou = muskingum_nonlinear_lanzhou(p["lanzhou"], upstream, mh, xt)
    xiaheyan = muskingum_nonlinear_xiaheyan(p["xiaheyan"], lanzhou)
    qingtongxia = muskingum_nonlinear_qingtongxia(p["qingtongxia"], xiaheyan)
    shizuishan = muskingum_nonlinear_shizuishan(p["shizuishan"], qingtongxia)
    bayangaole = muskingum_nonlinear_bayangaole(p["bayangaole"], shizuishan)
    sanhuhekou = muskingum_nonlinear_sanhuhekou(p["sanhuhekou"], bayangaole)
    baotou = muskingum_nonlinear_baotou(p["baotou"], sanhuhekou)
    toudaoguai = muskingum_nonlinear_toudaoguai(p["toudaoguai"], baotou)

    return {
        "兰州": lanzhou.tolist(),
        "下河沿": xiaheyan.tolist(),
        "青铜峡": qingtongxia.tolist(),
        "石嘴山": shizuishan.tolist(),
        "巴彦高勒": bayangaole.tolist(),
        "三湖河口": sanhuhekou.tolist(),
        "包头": baotou.tolist(),
        "头道拐": toudaoguai.tolist(),
    }

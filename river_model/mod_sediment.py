# -*- coding: utf-8 -*-
"""
mod_sediment.py — 输沙造床子模型（区间输沙 / 河床变形冲淤计算）

模型拆分模块 M3：承接"洪水演进"子模型输出的包头、头道拐断面流量过程，
基于水流连续、动量守恒与泥沙平衡方程，进行滩槽流量分配、输沙率计算
与床沙变形冲淤计算，得到各河段（重点包头—头道拐）的冲淤量。

来源：coupledModel.py run_sediment_model（未改动任何计算逻辑），
仅将 Excel 路径、输出目录、文件名所依赖的全局 flood_frequency 参数化。

接口：run_sediment(Q_baotou, Q_toudaoguai, base_xlsx=None,
                   save_output=False, output_dir=None, label="") -> dict
"""

import os

import numpy as np
import pandas as pd


def _default_base_xlsx():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "场次洪水过程", "断面参数.xlsx")


def run_sediment(Q_baotou, Q_toudaoguai, base_xlsx=None,
                 save_output=False, output_dir=None, label="", quiet=False):
    """输沙造床子模型统一入口。

    参数:
        Q_baotou:      包头断面流量序列（m³/s）
        Q_toudaoguai:  头道拐断面流量序列（m³/s）
        base_xlsx:     断面参数.xlsx 路径（可选，缺省取本模块同目录 场次洪水过程/断面参数.xlsx）
        save_output:   是否写出 Excel 汇总（可选）
        output_dir:    输出目录（可选，默认 输出文件）
        label:         输出文件名标识（可选，通常为重现期，如 "2年"）
        quiet:         是否静默（不打印控制台汇总）

    返回 dict:
        {
          "segments": [ {"段号", "段长(km)", "总冲淤量(m³)"} , ... ],
          "total": float,                 # 全河段合计冲淤量 (m³)
          "reach": {"in":"包头","out":"头道拐"},
          "series": {...}                 # 可选：各段逐时段冲淤（默认不返回，避免体积过大）
        }
    """
    if base_xlsx is None:
        base_xlsx = _default_base_xlsx()
    if not os.path.exists(base_xlsx):
        raise FileNotFoundError(f'未找到断面参数文件: {base_xlsx}')

    Q_in = np.array(Q_baotou, dtype=float)
    Q_out = np.array(Q_toudaoguai, dtype=float)
    T = len(Q_in)

    tbl_seg = pd.read_excel(base_xlsx, sheet_name="断面参数", header=0)
    tbl_sed = pd.read_excel(base_xlsx, sheet_name="输沙率", header=0)

    # ---- 输沙率 ----
    Qs_in = tbl_sed["包头输沙率(t/s)"].values[:T]
    Qs_out = tbl_sed["头道拐输沙率(t/s)"].values[:T]
    if np.all(pd.isna(Qs_out)):
        Qs_out = Qs_in * 0.95

    # ---- 断面参数 ----
    Nx = len(tbl_seg)
    L_seg = tbl_seg["段长(km)"].values * 1000
    Bc_seg = tbl_seg["主槽宽(m)"].values
    Bt_seg = tbl_seg["滩地宽(m)"].values
    Jc_seg = tbl_seg["主槽比降(0/000)"].values / 1000
    Jt_seg = tbl_seg["滩地比降(0/000)"].values / 1000
    nc_seg = tbl_seg["主槽糙率"].values
    nt_seg = tbl_seg["滩地糙率"].values
    Zc0_seg = tbl_seg["初始主槽床高(m)"].values
    Zt0_seg = tbl_seg["初始滩地床高(m)"].values

    # ---- 计算参数 ----
    g = 9.81
    gamma_s = 1.4e3
    omega_t = 2e-4
    K = 1.75
    Delta_t = 86400
    a_seg = 3.037
    b_seg = 0.979

    Q = np.zeros((Nx, T))
    Qs = np.zeros((Nx, T))
    Qc = np.zeros((Nx, T))
    Qt = np.zeros((Nx, T))
    Zc = np.zeros((Nx, T))
    Zt = np.zeros((Nx, T))
    DeltaZc = np.zeros((Nx, T))
    DeltaZt = np.zeros((Nx, T))
    total_seg = np.zeros((Nx, T))
    Zc[:, 0] = Zc0_seg
    Zt[:, 0] = Zt0_seg
    Q[0, :] = Q_in
    Qs[0, :] = Qs_in

    # 区间汇入
    Q_branch = np.zeros((Nx, T))
    Qs_branch = np.zeros((Nx, T))
    for tt in range(T):
        dq = (Q_out[tt] - Q_in[tt]) / Nx
        dqs = (Qs_out[tt] - Qs_in[tt]) / Nx
        Q_branch[:, tt] = dq
        Qs_branch[:, tt] = dqs

    def solve_flow_balance(Q_val, Bc, Bt, Jc, Jt, nc, nt, Zc, Zt):
        Ht = max(Q_val / ((Bc + Bt) * 10), 0.01)
        tol = 1e-3
        maxIt = 200
        for _ in range(maxIt):
            base_c = max(Zc - Zt + Ht, 1e-3)
            base_t = max(Ht, 1e-3)
            Qc_ = (Bc * np.sqrt(Jc) / nc) * base_c ** (5 / 3)
            Qt_ = (Bt * np.sqrt(Jt) / nt) * base_t ** (5 / 3)
            F = Qc_ + Qt_ - Q_val
            if abs(F) < tol:
                return Ht, True
            dQc = (5 / 3) * (Bc * np.sqrt(Jc) / nc) * base_c ** (2 / 3)
            dQt = (5 / 3) * (Bt * np.sqrt(Jt) / nt) * base_t ** (2 / 3)
            Ht = max(Ht - F / (dQc + dQt), 1e-3)
        return Ht, False

    for tt in range(1, T):
        for i in range(1, Nx):
            Q[i, tt] = Q[i - 1, tt] + Q_branch[i, tt]
            Qs[i, tt] = Qs[i - 1, tt] + Qs_branch[i, tt]
        for i in range(Nx):
            Ht, _ = solve_flow_balance(
                Q[i, tt], Bc_seg[i], Bt_seg[i], Jc_seg[i], Jt_seg[i],
                nc_seg[i], nt_seg[i], Zc[i, tt - 1], Zt[i, tt - 1])

            Qc[i, tt] = (Bc_seg[i] * np.sqrt(Jc_seg[i]) / nc_seg[i]) * \
                max(Zc[i, tt - 1] - Zt[i, tt - 1] + Ht, 1e-3) ** (5 / 3)
            Qt[i, tt] = (Bt_seg[i] * np.sqrt(Jt_seg[i]) / nt_seg[i]) * \
                max(Ht, 1e-3) ** (5 / 3)

            Qs_cap = a_seg * Q[i, tt] ** b_seg
            dz_main = max(Zc[i, tt - 1] - Zt[i, tt - 1], 1e-3)
            DeltaZc[i, tt] = (Qs[i, tt - 1] - Qs_cap) * Delta_t / \
                (Bc_seg[i] * dz_main * gamma_s)
            if Zc[i, tt - 1] <= Zt[i, tt - 1]:
                DeltaZc[i, tt] = 0.0

            Vt = Qt[i, tt] / (Bt_seg[i] * max(Ht, 1e-3))
            sedOut = Vt * Bt_seg[i] * omega_t
            sedIn_t = (Qs[i, tt - 1] - Qs_cap) * (1 / (1 + K))
            DeltaZt[i, tt] = (sedIn_t - sedOut) / \
                (Bt_seg[i] * max(Ht, 1e-3) * gamma_s)

            Zc[i, tt] = Zc[i, tt - 1] + DeltaZc[i, tt]
            Zt[i, tt] = Zt[i, tt - 1] + DeltaZt[i, tt]
            total_seg[i, tt] = total_seg[i, tt - 1] + \
                DeltaZc[i, tt] * Bc_seg[i] + DeltaZt[i, tt] * Bt_seg[i]

    # ---- 汇总 ----
    segments = []
    for i in range(Nx):
        segments.append({
            "段号": f"段{i + 1}",
            "段长(km)": float(L_seg[i] / 1000),
            "总冲淤量(m³)": float(total_seg[i, -1]),
        })
    total_sum = float(sum(total_seg[:, -1]))

    if not quiet:
        print("\n==== 各段冲淤（%d 段）==== " % Nx)
        for i in range(Nx):
            print(f"段{i + 1:2d} 长{L_seg[i] / 1000:6.2f} km  总冲淤{total_seg[i, -1]:10.2f} m3")
        print(f"全河段合计 {total_sum:12.2f} m3")

    # ---- 可选写出 Excel ----
    if save_output:
        if output_dir is None:
            output_dir = "输出文件"
        os.makedirs(output_dir, exist_ok=True)
        excel_path = os.path.join(output_dir, f"耦合冲淤过程_{label}一遇.xlsx")
        df_summary = pd.DataFrame(segments)
        total_row = {"段号": "全河段合计", "段长(km)": np.nan, "总冲淤量(m³)": total_sum}
        df_summary = pd.concat([df_summary, pd.DataFrame([total_row])], ignore_index=True)
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="冲淤汇总", index=False)
        if not quiet:
            print(f"\n冲淤汇总数据已保存至: {excel_path}")

    return {
        "segments": segments,
        "total": total_sum,
        "reach": {"in": "包头", "out": "头道拐"},
        "n_segments": Nx,
        "n_time": T,
    }

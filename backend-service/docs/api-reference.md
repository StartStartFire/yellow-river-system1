# Web 服务 API 参考文档

> 龙羊峡—刘家峡梯级水库多目标优化调度模型 Web 服务
> 基础路径：`http://127.0.0.1:18080`
>
> **实现状态**：
> - ✅ 已实现：健康检查、提交任务、任务状态、结果查询、任务列表、评价排名、评价缓存、WebSocket、回调接收
> - 🚧 部分实现：过程数据补拉（端点已注册，但 MATLAB 侧尚未推送 `process_data` 类型消息）
> - 📋 计划中：补充过程数据、WebSocket `process_data` 类型推送的完整前端展示

---

## 目录

- [1. 健康检查](#1-健康检查)
- [2. 提交优化任务](#2-提交优化任务)
- [3. 查询任务状态](#3-查询任务状态)
- [4. 获取优化结果](#4-获取优化结果)
- [5. 任务列表](#5-任务列表)
- [6. 补充过程数据](#6-补充过程数据)
- [7. 评价排名](#7-评价排名)
- [8. 获取评价结果](#8-获取评价结果)
- [9. WebSocket 实时订阅](#9-websocket-实时订阅)
- [10. MATLAB 回调接收](#10-matlab-回调接收)
- [附录：完整调用流程](#附录完整调用流程)
- [附录：常见错误码](#附录常见错误码)

---

## 1. 健康检查

检查服务与 MATLAB Engine 是否就绪。

```
GET /health
```

**响应示例：**

```json
{
  "status": "ok",
  "engine": "ready",
  "version": "1.0.0"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 固定为 `"ok"` |
| `engine` | string | `"ready"` 或 `"not started"` |
| `version` | string | API 版本号 |

---

## 2. 提交优化任务

提交一个 NSGA-II 或 PAEM 优化任务。任务异步执行，返回 `job_id` 用于后续查询。

```
POST /run
```

**请求体：**

```json
{
  "algorithm": "nsga2",
  "pop": 15,
  "iterate": 20,
  "M": 2,
  "Q_sediment": 1800.0,
  "K_mut": null,
  "crossover_rate": 0.9,
  "flag_xixian": "全无",
  "year_start": null,
  "year_end": null,
  "initial_water_level_longyangxia": null,
  "initial_water_level_liujiaxia": null,
  "ice_prevention_flows": null
}
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `algorithm` | string | `"nsga2"` | 算法：`"nsga2"` 或 `"paem"` |
| `pop` | int | `15` | 种群规模（方案数），≥1 |
| `iterate` | int | `20` | 进化代数，≥1 |
| `M` | int | `2` | 目标函数个数，≥1（2：发电量+缺水量；3：+协同度） |
| `Q_sediment` | float | `1800.0` | 冲沙流量 (m³/s)，≥0 |
| `K_mut` | int \| null | `null` | PAEM 变异参数，仅 `paem` 算法需要 |
| `crossover_rate` | float | `0.9` | 交叉概率 Pc，范围 [0, 1] |
| `flag_xixian` | string | `"全无"` | 西线调水方案：`"全无"` / `"全有"` / `"有上无下"` / `"有下无上"` |
| `year_start` | int \| null | `null` | 调度起始年份（如 2000），null=使用全部年份 |
| `year_end` | int \| null | `null` | 调度结束年份（如 2010），null=使用全部年份 |
| `initial_water_level_longyangxia` | float \| null | `null` | 龙羊峡起调水位 (m)（null=默认 2580） |
| `initial_water_level_liujiaxia` | float \| null | `null` | 刘家峡起调水位 (m)（null=默认 1720） |
| `ice_prevention_flows` | list[float] \| null | `null` | 防凌流量 [11月,12月,1月,2月,3月] (m³/s)（null=默认 [610,420,420,420,420]） |

**响应示例（任务已入队）：**

```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "progress_percent": 0.0,
  "created_at": "2026-07-29 15:33:26",
  "message": null
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `job_id` | string | 任务唯一标识（UUID） |
| `status` | string | 当前状态：`queued` → `running` → `completed` / `failed` |
| `progress_percent` | float \| null | 进度百分比（0~100） |
| `created_at` | string \| null | 任务创建时间 |
| `message` | string \| null | 状态描述信息 |

---

## 3. 查询任务状态

```
GET /status/{job_id}
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `job_id` | string | 任务 ID |

**响应示例（运行中）：**

```json
{
  "job_id": "a1b2c3d4-...",
  "status": "running",
  "progress_percent": 45.0,
  "created_at": "2026-07-29 15:33:26",
  "message": null
}
```

**响应示例（已完成）：**

```json
{
  "job_id": "a1b2c3d4-...",
  "status": "completed",
  "progress_percent": 100.0,
  "created_at": "2026-07-29 15:33:26",
  "message": "NSGA2 优化完成"
}
```

**状态流转：**

```
queued → running → completed
                  → failed
```

---

## 4. 获取优化结果

获取优化完成后的 Pareto 解集矩阵（chromosome）和 22 维评价指标矩阵（evaluating）。

```
GET /results/{job_id}
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `job_id` | string | 任务 ID |

**响应示例：**

```json
{
  "job_id": "a1b2c3d4-...",
  "status": "completed",
  "algorithm": "nsga2",
  "chromosome": [
    [2580.12, 2579.88, ..., 0.0005, 562.41, 1.0, 0.85],
    ...
  ],
  "evaluating": [
    [8.7998, 27.7850, 0.0074, 0.2074, 0.2000, 0.8204, ...],
    ...
  ],
  "objective_names": ["缺水量", "发电量", "协同度"],
  "message": "NSGA2 优化完成",
  "generated_at": "2026-07-29 15:33:26"
}
```

**chromosome 矩阵每行结构：**

| 列范围 | 内容 | 维度 |
|--------|------|------|
| `1:V/2` | 龙羊峡逐时段水位过程（54年×20时段） | 1080 列 |
| `V/2+1:V` | 刘家峡逐时段水位过程（54年×20时段） | 1080 列 |
| `V+1:V+M` | 目标函数值（发电量、缺水量等） | M 列 |
| `V+M+1` | 非支配排序等级（1=最优） | 1 列 |
| `V+M+2` | 拥挤距离 | 1 列 |

> **注意**：chromosome 行数可能多于 evaluating，chromosome 包含所有非支配排序后的种群个体，evaluating 仅含 pop 个方案的 22 个评价指标。Inf/NaN 值会被转为 `null`。

**evaluating 矩阵（22 个评价指标）：**

| 索引 | 指标 | 所属子系统 | 说明 |
|------|------|-----------|------|
| 0 | R1 | 水 | 龙羊峡水库水位最大变化幅度比 |
| 1 | R2 | 水 | 刘家峡水库水位最大变化幅度比 |
| 2 | R3 | 水 | 龙羊峡库空率 |
| 3 | R4 | 水 | 刘家峡库空率 |
| 4 | R5 | 水 | 龙羊峡库满率 |
| 5 | R6 | 水 | 刘家峡库满率 |
| 6 | R7 | 沙 | 宁蒙河段多年冲沙保证率 |
| 7 | R8 | 沙 | 宁蒙河段冲沙水量 |
| 8 | R9 | 能 | 龙羊峡发电保证率 |
| 9 | R10 | 能 | 刘家峡发电保证率 |
| 10 | R11 | 能 | 龙羊峡多年平均弃水率 |
| 11 | R12 | 能 | 刘家峡多年平均弃水率 |
| 12 | R13 | 能 | 梯级水库群最小出力比 |
| 13 | R14 | 灾 | 防洪期龙羊峡水库最大下泄流量 |
| 14 | R15 | 灾 | 防洪期刘家峡水库最大下泄流量 |
| 15 | R16 | 灾 | 刘家峡水库安全防凌流量偏离度 |
| 16 | R17 | 生 | 工业生活供水保证率 |
| 17 | R18 | 生 | 工业生活最大缺水率 |
| 18 | R19 | 生 | 农业供水保证率 |
| 19 | R20 | 生 | 农业最大缺水率 |
| 20 | R21 | 生 | 生态供水保证率 |
| 21 | R22 | 生 | 生态最大缺水率 |

---

## 5. 任务列表

获取所有任务列表，可按状态过滤。

```
GET /jobs
GET /jobs?status=completed
```

**查询参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `status` | string \| 可选 | 过滤状态：`queued` / `running` / `completed` / `failed` |

**响应示例：**

```json
[
  {
    "job_id": "a1b2c3d4-...",
    "status": "completed",
    "algorithm": "nsga2",
    "progress_percent": 100.0,
    "created_at": "2026-07-29 15:33:26"
  },
  {
    "job_id": "b2c3d4e5-...",
    "status": "running",
    "algorithm": "paem",
    "progress_percent": 45.0,
    "created_at": "2026-07-29 15:34:10"
  }
]
```

列表按创建时间倒序排列（最新的在前）。

---

## 6. 补充过程数据 🚧（部分实现）

> **当前状态**：`GET /process/{job_id}` 端点已注册，但 MATLAB 侧尚未推送 `type='process_data'` 消息，因此 `process_data` 字段始终为 `null`。
> 完整功能依赖 Phase E（MATLAB 过程透明化改造）完成。

当 WebSocket 连接较晚时，可通过此端点补拉最新过程数据（水位、流量、出力曲线等）。

```
GET /process/{job_id}
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `job_id` | string | 任务 ID |

**响应示例：**

```json
{
  "job_id": "a1b2c3d4-...",
  "status": "completed",
  "process_data": {
    "iteration": 20,
    "timestamp": "2026-07-29 15:33:26",
    "start_year": 2020,
    "longyang_level": [2580.1, 2579.8, ...],
    "liujia_level": [1720.2, 1719.5, ...],
    "longyang_outflow": [1200.5, 1150.3, ...],
    "liujia_outflow": [1350.2, 1280.7, ...],
    "longyang_power": [48.2, 46.5, ...],
    "liujia_power": [52.1, 50.3, ...],
    "total_power": [100.3, 96.8, ...],
    "water_shortage": [0.0, 0.0, 0.05, ...],
    "coordination": {
      "h_water": 0.85,
      "h_ele": 0.72,
      "h_sed": 0.68,
      "h_eco": 0.91
    }
  },
  "message": null
}
```

| 字段 | 说明 |
|------|------|
| `process_data` | 最近一次推送的过程数据，`null` 表示尚未生成 |
| `process_data.longyang_level` | 龙羊峡最近 n 年逐时段水位 (m) |
| `process_data.liujia_level` | 刘家峡最近 n 年逐时段水位 (m) |
| `process_data.longyang_outflow` | 龙羊峡下泄流量 (m³/s) |
| `process_data.liujia_outflow` | 刘家峡下泄流量 (m³/s) |
| `process_data.longyang_power` | 龙羊峡出力 (万 kW) |
| `process_data.liujia_power` | 刘家峡出力 (万 kW) |
| `process_data.total_power` | 梯级总出力 (万 kW) |
| `process_data.water_shortage` | 兰州断面缺水量 (亿 m³) |
| `process_data.coordination` | 各子系统多年平均有序度 |

---

## 7. 评价排名

对已完成优化任务的解集进行多算法排名评价。

```
POST /evaluate
```

**请求体：**

```json
{
  "job_id": "a1b2c3d4-...",
  "method": "ALL"
}
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `job_id` | string | — | 已完成的任务 ID |
| `method` | string | `"ALL"` | 评价方法：`"NMF"` / `"PP"` / `"AHP_FUZZY"` / `"ALL"` |

**方法说明：**

| 方法 | 全称 | 原理 | 适用场景 |
|------|------|------|---------|
| `NMF` | 非负矩阵分解布谷鸟搜索 | 矩阵分解 A≈W·H，按 H 权向量排名 | 无先验知识的数据驱动排名 |
| `PP` | 投影寻踪布谷鸟搜索 | 寻找最优投影方向 a\*，按投影值 z\* 排名 | 高维数据降维排名 |
| `AHP_FUZZY` | AHP 模糊综合评价 | 5 子系统先独立评、AHP 再综合 | 有领域知识（子系统权重已知）的场景 |
| `ALL` | **推荐** | 同时运行以上 3 种算法 + 序号总和理论整合 | 综合排名，避免单一算法偏差 |

### ALL 模式响应

```json
{
  "job_id": "a1b2c3d4-...",
  "method": "ALL",
  "status": "success",
  "ranking": [5, 9, 13, 1, 6, 0, 3, 14, 4, 8, 12, 11, 2, 7, 10],
  "details": {
    "method": "ALL",
    "status": "success",
    "convergence": {
      "NMF": [238833064.76, 133960174.19, ...],
      "PP": [0.0205, 0.0133, ...]
    },
    "rankings": [
      {
        "algorithm": "NMF",
        "ranks": [6, 12, 13, 1, 5, 0, 2, 14, 4, 8, 10, 11, 3, 7, 9],
        "scores": [5246.91, 5246.91, ...],
        "execution_time": 0.48
      },
      {
        "algorithm": "PP",
        "ranks": [5, 2, 13, 1, 7, 0, 4, 14, 6, 9, 12, 10, 3, 8, 11],
        "scores": [908.27, 908.28, ...],
        "execution_time": 0.94
      },
      {
        "algorithm": "AHP_FUZZY",
        "ranks": [5, 12, 13, 1, 6, 0, 3, 14, 4, 8, 11, 9, 2, 7, 10],
        "scores": [661.40, 661.36, ...],
        "execution_time": 0.01
      },
      {
        "algorithm": "ALL",
        "ranks": [5, 9, 13, 1, 6, 0, 3, 14, 4, 8, 12, 11, 2, 7, 10],
        "scores": null,
        "execution_time": null
      }
    ],
    "radar": {
      "indicators": [
        {"name": "NMF", "max": 5246.93},
        {"name": "PP", "max": 908.31},
        {"name": "AHP_FUZZY", "max": 661.60}
      ],
      "plans": [
        {"plan": "方案1", "values": [5246.93, 908.31, 661.60]},
        {"plan": "方案2", "values": [5246.93, 908.31, 661.60]},
        ...
      ]
    },
    "raw_indicators": {
      "subsystems": [
        {"name": "水子系统", "indices": [0, 1, 2, 3, 4, 5]},
        {"name": "沙子系统", "indices": [6, 7]},
        {"name": "能子系统", "indices": [8, 9, 10, 11, 12]},
        {"name": "灾子系统", "indices": [13, 14, 15]},
        {"name": "生子系统", "indices": [16, 17, 18, 19, 20, 21]}
      ],
      "schemes": [
        {
          "plan": "方案1",
          "values": [8.80, 27.78, 0.007, 0.207, 0.200, 0.820, 0.259, 10.02, ...]
        },
        ...
      ]
    }
  }
}
```

### 单算法模式响应（以 NMF 为例）

```json
{
  "job_id": "a1b2c3d4-...",
  "method": "NMF",
  "status": "success",
  "ranking": [6, 12, 13, 1, 5, 0, 2, 14, 4, 8, 10, 11, 3, 7, 9],
  "scores": [5246.91, 5246.91, ...],
  "best_scheme_index": 5,
  "details": {
    "method": "NMF",
    "status": "success",
    "convergence": {
      "NMF": [238833064.76, 133960174.19, ...]
    },
    "rankings": [
      {
        "algorithm": "NMF",
        "ranks": [6, 12, ...],
        "scores": [5246.91, ...],
        "execution_time": 0.48
      }
    ],
    "radar": {
      "indicators": [{"name": "NMF", "max": 5246.93}],
      "plans": [{"plan": "方案1", "values": [5246.93]}, ...]
    }
  }
}
```

### 返回字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `job_id` | string | 任务 ID |
| `method` | string | 评价方法 |
| `status` | string | `"success"` 或 `"error"` |
| `ranking` | list[int] \| null | 最终排名数组（0-indexed，0=最优），如 `[5,9,...]` 表示方案 6 排第 1、方案 10 排第 2 |
| `scores` | list[float] \| null | 各方案得分（仅单算法模式） |
| `best_scheme_index` | int \| null | 最优方案索引（0-based，仅单算法模式） |
| `details` | dict \| null | 详细数据（供前端图表使用） |
| `details.convergence` | dict | NMF/PP 收敛曲线（各 500 个适应度值） |
| `details.rankings` | list | 各算法排名表（含算法名、排名数组、得分、耗时） |
| `details.radar` | dict | 雷达图数据（indicators + plans） |
| `details.raw_indicators` | dict \| null | 前 10 名方案的 22 个原始评价指标（按子系统分组） |

### 排名解读说明

> `ranking` 数组长度为方案数（pop 值），`ranking[i]` 表示**方案 i** 的排名（0-indexed）。
>
> 例如 `ranking = [5, 9, ...]` 表示：
> - 方案 0 → 排名第 6（即第 6 优）
> - 方案 1 → 排名第 10（即第 10 优）
> - 求和最小的方案 = `argmin(ranking)` → 最优方案

### 算法得分解读

| 算法 | 得分字段 | 含义 |
|------|---------|------|
| NMF | `H`（权向量） | 越大越优 |
| PP | `z`（投影值） | 越大越优 |
| AHP_FUZZY | `final_scores`（最终得分） | 越大越优 |
| ALL | 序号总和 | **越小越优**（排名之和） |

---

## 8. 获取评价结果

获取已缓存的评价结果（无需重新计算）。

```
GET /evaluate/{job_id}
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `job_id` | string | 任务 ID |

**响应示例：**

```json
{
  "job_id": "a1b2c3d4-...",
  "status": "evaluated",
  "method": "ALL",
  "convergence": {...},
  "rankings": [...],
  "radar": {...},
  "raw_indicators": {...}
}
```

若尚未评价，返回：

```json
{
  "job_id": "a1b2c3d4-...",
  "status": "not_evaluated",
  "message": "尚未进行评价"
}
```

---

## 9. WebSocket 实时订阅

在优化任务执行过程中，通过 WebSocket 实时接收进度推送。

```
WS /ws/{job_id}
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `job_id` | string | 任务 ID |

**连接方式（JavaScript 示例）：**

```javascript
const ws = new WebSocket('ws://127.0.0.1:18080/ws/a1b2c3d4-...');
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  // msg.type: "progress" | "process_data"
  // msg.timestamp: "2026-07-29 15:33:26"
};
```

**推送消息格式（progress 类型 - 每 10 代推送一次）：**

```json
{
  "type": "progress",
  "job_id": "a1b2c3d4-...",
  "timestamp": "2026-07-29 15:33:26",
  "payload": {
    "iteration": 10,
    "timestamp": "2026-07-29 15:33:26",
    "progress_percent": 50.0,
    "best_objectives": [2.707, 562.41],
    "avg_objectives": [2.720, 562.55],
    "objective_std": [0.015, 0.12],
    "pareto_size": 5,
    "avg_crowding_distance": 0.85,
    "pareto_objectives": [[2.707, 562.41], [2.721, 562.62], ...]
  }
}
```

**推送消息格式（process_data 类型 - 每 10 代推送一次）：**

```json
{
  "type": "process_data",
  "job_id": "a1b2c3d4-...",
  "timestamp": "2026-07-29 15:33:26",
  "payload": {
    "iteration": 10,
    "timestamp": "2026-07-29 15:33:26",
    "start_year": 2020,
    "longyang_level": [2580.1, 2579.8, ...],
    "liujia_level": [1720.2, 1719.5, ...],
    "longyang_outflow": [1200.5, ...],
    "liujia_outflow": [1350.2, ...],
    "longyang_power": [48.2, ...],
    "liujia_power": [52.1, ...],
    "total_power": [100.3, ...],
    "water_shortage": [0.0, ...],
    "coordination": {
      "h_water": 0.85,
      "h_ele": 0.72,
      "h_sed": 0.68,
      "h_eco": 0.91
    }
  }
}
```

| payload 字段 | 说明 |
|-------------|------|
| `best_objectives` | 当前最优个体的各目标值 |
| `avg_objectives` | 种群各目标均值 |
| `objective_std` | 种群各目标标准差 |
| `pareto_size` | 非支配解个数 |
| `avg_crowding_distance` | 平均拥挤距离 |
| `pareto_objectives` | 所有 Pareto 解的目标值矩阵 |

> **提示**：WebSocket 连接应在 POST /run 之前或之后立即建立，以免错过早期推送。若连接较晚，可通过 `GET /process/{job_id}` 补拉最新数据。

---

## 10. MATLAB 回调接收

MATLAB 在优化过程中通过 `webwrite` 调用此端点推送进度数据。**一般不需要手动调用。**

```
POST /cb
```

**请求体（由 MATLAB 的 http_callback_push.m 自动发送）：**

```json
{
  "type": "progress",
  "data": {
    "job_id": "a1b2c3d4-...",
    "iteration": 10,
    "timestamp": "2026-07-29 15:33:26",
    "progress_percent": 50.0,
    "best_objectives": [2.707, 562.41],
    ...
  }
}
```

**响应：**

```json
{
  "received": true,
  "job_id": "a1b2c3d4-..."
}
```

---

## 附录：完整调用流程

### 用户交互时序

```
用户                    前端                     后端 API                    MATLAB
 │                      │                        │                          │
 │  ① 点击"运行"        │                        │                          │
 │─────────────────────►│                        │                          │
 │                      │  ② POST /run           │                          │
 │                      │───────────────────────►│                          │
 │                      │                        │  ③ 返回 job_id + queued │
 │                      │◄───────────────────────│                          │
 │                      │                        │                          │
 │                      │  ④ WS /ws/{job_id}     │  ⑤ 后台队列出队         │
 │                      │══════════════════════►│═════════════════════════►│
 │                      │                        │  ⑥ load_data + 运行优化 │
 │                      │                        │◄════════════════════════│
 │                      │  ⑦ WS 推送 progress    │                          │
 │                      │◄═══════════════════════│                          │
 │                      │  ⑧ 更新进度条          │                          │
 │                      │                        │                          │
 │                      │  ⑨ 优化完成            │                          │
 │                      │◄═══════════════════════│                          │
 │                      │                        │                          │
 │  ⑩ 查看结果          │                        │                          │
 │─────────────────────►│                        │                          │
 │                      │  ⑪ GET /results/{id}   │                          │
 │                      │───────────────────────►│                          │
 │                      │◄───────────────────────│                          │
 │                      │  返回 chromosome +     │                          │
 │                      │  evaluating 矩阵       │                          │
 │                      │                        │                          │
 │  ⑫ 评价排名          │                        │                          │
 │─────────────────────►│                        │                          │
 │                      │  ⑬ POST /evaluate      │                          │
 │                      │───────────────────────►│                          │
 │                      │                        │  ⑭ evaluation_system    │
 │                      │                        │    NMF + PP + AHP-FUZZY │
 │                      │                        │    序号总和整合         │
 │                      │◄───────────────────────│                          │
 │                      │  ⑮ 返回排名+雷达图     │                          │
 │◄─────────────────────│  + 原始指标             │                          │
```

### 典型 curl 调用序列

```bash
# 1. 健康检查
curl http://127.0.0.1:18080/health

# 2. 提交优化任务
curl -X POST http://127.0.0.1:18080/run \
  -H "Content-Type: application/json" \
  -d '{"algorithm":"nsga2","pop":15,"iterate":5,"M":2,"Q_sediment":1800}'

# 3. 轮询任务状态（替换为实际 job_id）
curl http://127.0.0.1:18080/status/a1b2c3d4-...

# 4. 获取优化结果
curl http://127.0.0.1:18080/results/a1b2c3d4-...

# 5. 评价排名
curl -X POST http://127.0.0.1:18080/evaluate \
  -H "Content-Type: application/json" \
  -d '{"job_id":"a1b2c3d4-...","method":"ALL"}'

# 6. 获取缓存的评价结果
curl http://127.0.0.1:18080/evaluate/a1b2c3d4-...
```

---

## 附录：常见错误码

| HTTP 状态码 | 说明 | 常见原因 |
|------------|------|---------|
| **200** | 成功 | — |
| **400** | 请求参数错误 | 任务未完成就调 evaluate、算法名不合法、缺少必要参数 |
| **404** | 资源不存在 | `job_id` 不存在 |
| **500** | 服务内部错误 | MATLAB Engine 启动失败、评价系统导入失败 |
| **503** | 服务未就绪 | Engine 正在启动或已关闭 |

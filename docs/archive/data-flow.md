# 数据链路 — 全过程数据流向

> 📋 **目标状态设计（尚未完全实现）**
>
> 本文档描述的是过程透明化功能完成后的数据流向。
> **当前实现状态**：
> - ✅ MATLAB → JSONL 文件（每代写入，已完成）
> - ✅ MATLAB → POST /cb type='progress'（每 10 代推送汇总指标，已完成）
> - ✅ MATLAB → POST /cb type='process_data'（每 10 代推送过程数据，已完成；由 `push_callback_data.m` 统一封装）
> - ✅ 后端 /cb 端点接收（已完成）
> - ✅ 后端 /cb 区分两种 type 分别处理（已完成）
> - ✅ 后端 process_data 存储供 GET /process 补拉（已完成）
> - ✅ WebSocket 广播（已完成）
> - ✅ 前端 WS 接收 process_data 并更新图表（已完成）
> - ⬜ 前端 GET /process 补拉（后端端点已就绪，前端当前未接入，仅依赖 WS 实时推送）
>
> 具体实施细节见 [process-transparent-plan.md](process-transparent-plan.md)。

---

## 一、总览

```
MATLAB (nsga_2_para.m / PAEM_para.m)
  │
  │ 每代: write_json_log → NSGA2_progress.jsonl（文件持久化）
  │
  │ 每 10 代（含最后一代）:
  │
  ├─ http_callback_push('progress', summary_data)
  │   └─ POST /cb: payload.type == 'progress'
  │       └─ FastAPI → asyncio.Queue → broadcast_loop → WebSocket
  │           → 前端 handleWsMessage → 更新收敛曲线/进度/日志
  │
  ├─ http_callback_push('process_data', process_data)
  │   └─ POST /cb: payload.type == 'process_data'
  │       ├─ 存储到 JobRecord.process_data（供 GET /process 补拉）
  │       └─ asyncio.Queue → broadcast_loop → WebSocket
  │           → 前端 handleWsMessage → 更新水位/流量/出力图
  │
  └─ 最终结果: output.chromosome / chromosome_acc
      └─ services/matlab.py _extract_chromosome → TaskResult
          └─ JobManager → GET /results/{job_id}
              → 前端调用 getResults → 展示 Pareto 解集
```

---

## 二、type='progress' — 汇总指标（每 10 代推送）

### 2.1 MATLAB 侧（nsga_2_para.m）

MATLAB 每 10 代从当前种群计算汇总指标，通过 `http_callback_push('progress', summary_data)` 推送。`summary_data` 包含：

| 字段 | 说明 |
|------|------|
| `iteration` | 当前代数 |
| `timestamp` | 时间戳 |
| `progress_percent` | 进度百分比 |
| `best_objectives` | 最优个体各目标值 |
| `avg_objectives` | 种群各目标均值 |
| `objective_std` | 种群各目标标准差 |
| `pareto_size` | Pareto 前沿个体数 |
| `avg_crowding_distance` | 种群平均拥挤距离 |
| `pareto_objectives` | 所有 Pareto 解目标值矩阵 |

### 2.2 后端处理

后端 `/cb` 端点收到 `type='progress'` 消息后，打包为信封格式写入 `asyncio.Queue`，由 `broadcast_loop` 后台协程消费并广播到 WebSocket。

### 2.3 前端消费

前端 `ProcessTransparentView.vue` 通过 WebSocket 接收 `progress` 消息，更新进度条、收敛曲线、目标趋势和运行日志。

### 2.4 数据对应关系

| 前端组件 | MATLAB 字段 | 说明 |
|---------|-------------|------|
| 进度条 | `summary_data.progress_percent` | 计算方式: `round(i/iterate*100)` |
| 收敛曲线 - 缺水量 | `summary_data.best_objectives[0]` | f1 最优值 |
| 收敛曲线 - 发电量 | `summary_data.best_objectives[1]` | f2 最优值（负值，前端取绝对值） |
| 目标趋势 - 防洪 | `summary_data.best_objectives[0]` | 同收敛曲线缺水量 |
| 目标趋势 - 发电 | `summary_data.best_objectives[1]` | 同收敛曲线发电量 |
| 运行日志 | `best_objectives + pareto_size` | 格式化字符串 |

---

## 三、type='process_data' — 过程数据（每 10 代推送）

### 3.1 MATLAB 侧（nsga_2_para.m）

MATLAB 每 10 代（含最后一代）经 `push_callback_data.m` 选出代表性最优解（Pareto 前沿上拥挤度最大的个体），调用 `evaluate_objective_NSGA2` 获取完整过程变量，推送 `process_data`（内部经 `http_callback_push`）。过程数据覆盖**全部年份**（`n_years = Y`，非仅最近 10 年）。`process_data` 包含：

| 字段 | 来源 | 说明 |
|------|------|------|
| `iteration` | 当前代数 | — |
| `start_year` | `year_start + BASE_YEAR - 1` | 过程数据起始年份 |
| `longyang_level` | 决策变量前 V/2 列 | 龙羊峡逐时段水位 |
| `liujia_level` | 决策变量后 V/2 列 | 刘家峡逐时段水位 |
| `longyang_outflow` | `results.Long.Qout` | 龙羊峡出库流量 |
| `liujia_outflow` | `results.Liu.Qout` | 刘家峡出库流量 |
| `longyang_power` | `results.N.Ntii_long` | 龙羊峡出力 |
| `liujia_power` | `results.N.Ntii_liu` | 刘家峡出力 |
| `total_power` | `results.N.Etii_longliu` | 梯级总出力 |
| `water_shortage` | `results.liuzhou.Qshortage` | 兰州断面缺水量 |
| `coordination` | `results.coordination` 各项均值 | 四子系统多年平均有序度（h_water/h_ele/h_sed/h_eco） |
| `constraint` | 由缺水/生态/出力统计 | 约束满足率（water/eco/power_guarantee + combined_rate，0~100） |

### 3.2 后端处理

后端 `/cb` 端点收到 `type='process_data'` 消息后，同时执行两个动作：
1. 存储到 `JobRecord.process_data` 供 `GET /process/{job_id}` 补拉
2. 打包为信封格式写入 `asyncio.Queue`，广播到 WebSocket

### 3.3 前端消费 — WebSocket（实时）

前端收到 `process_data` 消息后，更新水位图、流量图、出力图等图表数据。

### 3.4 前端消费 — GET /process 补拉（未接入）

> 后端 `GET /process/{job_id}` 端点已就绪（返回 `JobRecord.process_data`），但**前端当前未实现该补拉调用**（`src/api/index.ts` 无对应函数），页面完全依赖 WS 实时推送。若 WS 连接晚于任务启动，将错过此前的推送；后续可按需接入补拉。

### 3.5 数据对应关系

| 前端组件 | MATLAB 来源 | 说明 |
|---------|-------------|------|
| 龙羊峡水位图 | `best_x(1:V/2)` 取全系列（n_years=Y） | 决策变量前 1080/2 列 |
| 刘家峡水位图 | `best_x(V/2+1:V)` 取全系列（n_years=Y） | 决策变量后 1080/2 列 |
| 龙羊峡出库流量 | `results.Long.Qout` 取全系列（n_years=Y） | `evaluate_objective_NSGA2` 计算的出库流量过程 |
| 刘家峡出库流量 | `results.Liu.Qout` 取全系列（n_years=Y） | 同上 |
| 龙羊峡出力 | `results.N.Ntii_long` 取全系列（n_years=Y） | `evaluate_objective_NSGA2` 计算的各电站出力 |
| 刘家峡出力 | `results.N.Ntii_liu` 取全系列（n_years=Y） | 同上 |
| 梯级总发电量 | `results.N.Etii_longliu` 取全系列（n_years=Y） | 所有梯级电站发电量之和 |
| 兰州缺水量 | `results.liuzhou.Qshortage` 取全系列（n_years=Y） | 各时段兰州断面缺水量 |

---

## 四、GET /results — 最终结果

### 4.1 MATLAB 侧

```matlab
output.chromosome = chromosome;  % pop × (V+M+2) 矩阵
% → Python services/matlab.py（MatlabExecutor）接收为 dict
% → _extract_chromosome 提取 chromosome 字段
% → 清洗 Inf/NaN → None → JSON null
```

### 4.2 前端消费

> 前端当前**未调用** `GET /results/{job_id}`（`src/api/index.ts` 无 getResults 函数）。
> 结果消费的实际路径是：过程透明页完成后跳转评价决策页，经 `POST /evaluate`（排名/雷达图/原始指标）与 `GET /decision/{job_id}`（逐方案过程曲线/目标满足度/水量分配）展示。
> `GET /results` 供 curl 调试与脚本使用。

响应结构（供脚本参考）：

```json
{
  "job_id": "xxx",
  "status": "completed",
  "algorithm": "nsga2",
  "chromosome": [[...], ...],  // pop × (V+M+2) 矩阵
  "evaluating": [[...], ...],  // pop × 22 评价指标矩阵
  "objective_names": ["缺水量", "发电量", "协同度"],
  "message": "NSGA2 优化完成",
  "generated_at": "2026-07-11 12:00"
}
```

### 4.3 Pydantic 模型定义

后端 `schemas/result.py` 中定义 `ResultResponse` 模型，详见 [api-reference.md](../../backend-service/docs/api-reference.md#4-获取优化结果)。

---

## 五、数据真实性审查

| 数据类型 | MATLAB 来源 | 传输路径 | 前端变量 | 是否真实 |
|---------|-------------|---------|---------|---------|
| 进度百分比 | `round(i/iterate*100)` | progress → WS | `progress` | ✅ |
| 迭代次数 | `i` | progress → WS | 收敛曲线 x 轴 | ✅ |
| 缺水量最优值 | `min(obj_values(:,1))` | progress → WS | `fitness`, `flood` | ✅ |
| 发电量最优值 | `min(obj_values(:,2))` | progress → WS | `power` | ✅ |
| 目标标准差 | `std(obj_values)` | progress → WS | 未展示 | ✅ 但未用 |
| Pareto 前沿大小 | `sum(rank==1)` | progress → WS | 日志中显示 | ✅ |
| Pareto 前沿目标值 | `obj_values(pareto_mask,:)` | progress → WS | 未展示 | ✅ 但未用 |
| 龙羊峡水位 | `best_x(1:V/2)` | process_data → WS（后端另存供 GET /process，前端暂未接入） | `longyang.optimal` | ✅ |
| 刘家峡水位 | `best_x(V/2+1:V)` | process_data → WS（后端另存供 GET /process，前端暂未接入） | `liujia.optimal` | ✅ |
| 龙羊峡出库流量 | `results.Long.Qout` | process_data → WS（后端另存供 GET /process，前端暂未接入） | `longyang.optimal` | ✅ |
| 刘家峡出库流量 | `results.Liu.Qout` | process_data → WS（后端另存供 GET /process，前端暂未接入） | `liujia.optimal` | ✅ |
| 龙羊峡出力 | `results.N.Ntii_long` | process_data → WS（后端另存供 GET /process，前端暂未接入） | `longyang.optimal` | ✅ |
| 刘家峡出力 | `results.N.Ntii_liu` | process_data → WS（后端另存供 GET /process，前端暂未接入） | `liujia.optimal` | ✅ |
| 梯级总发电量 | `results.N.Etii_longliu` | process_data → WS（后端另存供 GET /process，前端暂未接入） | 未展示 | ✅ 但未用 |
| 兰州缺水量 | `results.liuzhou.Qshortage` | process_data → WS（后端另存供 GET /process，前端暂未接入） | 未展示 | ✅ 但未用 |
| 最终 chromosome | `output.chromosome` | GET /results | `getResults()` | ✅ |
| 预报/历史对照线 | — | — | `forecast/history/schedule` | ❌ 模型不生成 |
| 装机容量 | — | — | `capacity` | ❌ 模型不推送 |
| 约束满足状态 | — | — | `summary.constraintStatus` | ❌ 未推送 |
| 预估结果摘要 | — | — | `summary.estimatedResult` | ❌ 未推送 |
| 最优方案摘要 | — | — | `summary.bestSolution` | ❌ 未推送 |

---

## 六、文件变更索引

| 链路环节 | 关键文件 | 说明 |
|---------|---------|------|
| MATLAB 推送 | `matlab-model/nsga_2_para.m` | 进化循环每 10 代调用 `push_callback_data`（NSGA-II 版回调块约 L95-100） |
| MATLAB 推送 | `matlab-model/PAEM_para.m` | 同上，PAEM 版本 |
| MATLAB 工具 | `matlab-model/push_callback_data.m` | 回调数据统一封装（汇总指标 + 代表性解过程数据） |
| MATLAB 工具 | `matlab-model/find_representative_solution.m` | 选代表性最优解 |
| MATLAB 工具 | `matlab-model/http_callback_push.m` | webwrite POST 封装 |
| 后端接收 | `backend-service/app/api/callback.py` | /cb 端点区分两种 type |
| 后端存储 | `backend-service/app/core/job_manager.py` | JobRecord.process_data |
| 后端查询 | `backend-service/app/api/jobs.py` | GET /process/{job_id} |
| 后端推送 | `backend-service/app/core/websocket.py` | broadcast_loop |
| 后端模型 | `backend-service/app/schemas/callback.py` | CallbackPayload, CallbackResponse |
| 模型评估 | `matlab-model/evaluate_objective_NSGA2.m` | `if nargout>1` 返回 results |
| 模型评估 | `matlab-model/evaluate_objective_PAEM.m` | 同上 |
| 模型评估 | `matlab-model/evaluate_objective.m` | 同上 |
| 前端接收 | `frontend-service/.../ProcessTransparentView.vue` | WS 消息处理（progress + process_data） |
| 前端 API | `frontend-service/src/api/index.ts` | postRun + postEvaluate + getEvaluateResult + getDecisionPlans |
| 前端类型 | `frontend-service/src/types/process.ts` | ProcessDataResponse + SummaryMetrics |

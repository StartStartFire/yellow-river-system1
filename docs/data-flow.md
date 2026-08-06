# 数据链路 — 全过程数据流向

> 📋 **目标状态设计（尚未完全实现）**
>
> 本文档描述的是过程透明化功能完成后的数据流向。
> **当前实现状态**：
> - ✅ MATLAB → JSONL 文件（每代写入，已完成）
> - ✅ MATLAB → POST /cb type='progress'（每 10 代推送汇总指标，已完成）
> - ⬜ MATLAB → POST /cb type='process_data'（阶段 E 待实施）
> - ✅ 后端 /cb 端点接收（已完成）
> - ✅ WebSocket 广播（已完成）
> - ⬜ 后端 /cb 区分两种 type 分别处理（阶段 F 待实施）
> - ⬜ 前端 WS 接收 process_data 并更新图表（阶段 G 待实施）
>
> 具体实施计划见 [process-transparent-plan.md](process-transparent-plan.md)。

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

```matlab
summary_data.iteration = i;                    % 当前代数
summary_data.timestamp = '2026-07-11 12:00';  % 时间戳
summary_data.progress_percent = 50.0;          % 进度百分比

% 汇总统计
summary_data.best_objectives = [0.5, 450];     % [缺水量最小, 发电量最小(负值)]
summary_data.avg_objectives = [1.2, 430];      % [缺水量平均, 发电量平均]
summary_data.objective_std = [0.3, 25];        % [缺水量标准差, 发电量标准差]
summary_data.pareto_size = 8;                  % Pareto 前沿个体数

% Pareto 前沿个体目标值（用于前端绘制实时 Pareto 散点图）
summary_data.pareto_objectives = [
  [0.5, 450],
  [0.6, 445],
  ...
];
```

### 2.2 后端处理（main.py /cb 端点）

```python
if payload.type == 'progress':
    envelope = build_envelope(payload, job_id=cb_job_id)
    await callback_queue.put(envelope)
    # → broadcast_loop → WebSocket 推送
```

### 2.3 前端消费（ProcessTransparentView.vue）

```javascript
// 处理 progress 消息
const handleWsMessage = (msg: any) => {
  if (msg.type === 'progress' && msg.payload) {
    const d = msg.payload
    progress.value = d.progress_percent

    // 收敛曲线数据
    convergenceData.value.iterations.push(d.iteration)
    convergenceData.value.fitness.push(d.best_objectives[0])  // 缺水量收敛

    // 目标趋势数据
    objectiveTrendData.value.iterations.push(d.iteration)
    objectiveTrendData.value.flood.push(d.best_objectives[0])
    objectiveTrendData.value.power.push(d.best_objectives[1])

    // 运行日志
    logsDisplay.value.unshift({
      time, level: 'INFO',
      message: `代 ${d.iteration}，最优: [${d.best_objectives}], 前沿: ${d.pareto_size} 个`,
    })
  }
}
```

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

```matlab
% 选代表性最优解（Pareto 前沿上拥挤度最大的个体）
best_idx = find_representative_solution(chromosome, pop, V, M);
best_x = chromosome(best_idx, 1:V);

% 调用 evaluate 获取 results（含过程变量）
[~, results] = evaluate_objective_NSGA2(best_x, V, M, Q_sediment);

% 只取最近 10 年
n_years = min(10, Y);
year_start = Y - n_years + 1;

process_data.iteration = i;                    % 当前代数
process_data.timestamp = current_time;         % 时间戳

% 决策变量直接提取（前 V/2 = 龙羊峡, 后 V/2 = 刘家峡）
process_data.longyang_level = long_x(sidx:eidx)';   % 龙羊峡水位
process_data.liujia_level = liu_x(sidx:eidx)';      % 刘家峡水位

% 从 results 结构体提取过程变量（取最近 n_years 年）
process_data.longyang_outflow = reshape(results.Long.Qout(yr, :)', 1, []);
process_data.liujia_outflow = reshape(results.Liu.Qout(yr, :)', 1, []);
process_data.longyang_power = reshape(results.N.Ntii_long(yr, :)', 1, []);
process_data.liujia_power = reshape(results.N.Ntii_liu(yr, :)', 1, []);
process_data.total_power = reshape(results.N.Etii_longliu(yr, :)', 1, []);
process_data.water_shortage = reshape(results.liuzhou.Qshortage(yr, :)', 1, []);
```

### 3.2 后端处理（main.py /cb 端点）

```python
elif payload.type == 'process_data':
    # 存储到后端供补拉
    if job_manager and cb_job_id:
        record = job_manager.get_status(cb_job_id)
        if record:
            record.process_data = payload.data
    # 同时也推送到 WebSocket
    envelope = build_envelope(payload, job_id=cb_job_id)
    await callback_queue.put(envelope)
```

### 3.3 前端消费 — WebSocket（实时）

```javascript
if (msg.type === 'process_data' && msg.payload) {
  const pd = msg.payload
  // 更新时间标签
  const labels = pd.longyang_level.map((_, i) => `时段${i + 1}`)

  // 水位图（optimal 线）
  waterLevelData.value = {
    dates: labels,
    longyang: { optimal: pd.longyang_level, forecast: [], history: [] },
    liujia: { optimal: pd.liujia_level, forecast: [], history: [] },
  }
  // 流量图
  dischargeData.value = { ... }
  // 出力图
  powerOutputData.value = { ... }
}
```

### 3.4 前端消费 — GET /process 补拉（页面初始化）

```javascript
// 页面加载时补拉（针对 WebSocket 连接晚于第一次推送的情况）
const fetchProcessData = async () => {
  const res = await fetch(`http://127.0.0.1:18080/process/${jobId}`)
  const data = await res.json()
  if (data.process_data) {
    // 更新水位、流量、出力数据（同上）
  }
}
```

### 3.5 数据对应关系

| 前端组件 | MATLAB 来源 | 说明 |
|---------|-------------|------|
| 龙羊峡水位图 | `best_x(1:V/2)` 取最近 10 年 | 决策变量前 1080/2 列 |
| 刘家峡水位图 | `best_x(V/2+1:V)` 取最近 10 年 | 决策变量后 1080/2 列 |
| 龙羊峡出库流量 | `results.Long.Qout` 取最近 10 年 | `evaluate_objective_NSGA2` 计算的出库流量过程 |
| 刘家峡出库流量 | `results.Liu.Qout` 取最近 10 年 | 同上 |
| 龙羊峡出力 | `results.N.Ntii_long` 取最近 10 年 | `evaluate_objective_NSGA2` 计算的各电站出力 |
| 刘家峡出力 | `results.N.Ntii_liu` 取最近 10 年 | 同上 |
| 梯级总发电量 | `results.N.Etii_longliu` 取最近 10 年 | 所有梯级电站发电量之和 |
| 兰州缺水量 | `results.liuzhou.Qshortage` 取最近 10 年 | 各时段兰州断面缺水量 |

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

```javascript
// api/index.ts
export async function getResults(jobId: string): Promise<ResultResponse> {
  const res = await fetch(`${API_BASE}/results/${jobId}`)
  return res.json()
}
// 响应结构:
{
  "job_id": "xxx",
  "status": "completed",
  "algorithm": "nsga2",
  "chromosome": [[...], ...],  // pop × (V+M+2) 矩阵
  "objective_names": ["缺水量", "发电量", "协同度"],
  "message": "NSGA2 优化完成",
  "generated_at": "2026-07-11 12:00"
}
```

### 4.3 Pydantic 模型定义

```python
class ResultResponse(BaseModel):
    job_id: str
    status: str
    algorithm: str
    chromosome: list[list[float | None]] | None = None
    objective_names: list[str] = ["缺水量", "发电量", "协同度"]
    message: str | None = None
    generated_at: str | None = None
```

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
| 龙羊峡水位 | `best_x(1:V/2)` | process_data → WS + GET | `longyang.optimal` | ✅ |
| 刘家峡水位 | `best_x(V/2+1:V)` | process_data → WS + GET | `liujia.optimal` | ✅ |
| 龙羊峡出库流量 | `results.Long.Qout` | process_data → WS + GET | `longyang.optimal` | ✅ |
| 刘家峡出库流量 | `results.Liu.Qout` | process_data → WS + GET | `liujia.optimal` | ✅ |
| 龙羊峡出力 | `results.N.Ntii_long` | process_data → WS + GET | `longyang.optimal` | ✅ |
| 刘家峡出力 | `results.N.Ntii_liu` | process_data → WS + GET | `liujia.optimal` | ✅ |
| 梯级总发电量 | `results.N.Etii_longliu` | process_data → WS + GET | 未展示 | ✅ 但未用 |
| 兰州缺水量 | `results.liuzhou.Qshortage` | process_data → WS + GET | 未展示 | ✅ 但未用 |
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
| MATLAB 推送 | `matlab-model/nsga_2_para.m` | 第 77-150 行：每 10 代推送两种消息 |
| MATLAB 推送 | `matlab-model/PAEM_para.m` | 同上，PAEM 版本 |
| MATLAB 工具 | `matlab-model/find_representative_solution.m` | 选代表性最优解 |
| MATLAB 工具 | `matlab-model/http_callback_push.m` | webwrite POST 封装 |
| 后端接收 | `backend-service/app/api/callback.py` | /cb 端点区分两种 type |
| 后端存储 | `backend-service/app/job_manager.py:31` | JobRecord.process_data |
| 后端查询 | `backend-service/app/api/jobs.py` | GET /process/{job_id} |
| 后端推送 | `backend-service/app/websocket.py` | broadcast_loop |
| 后端模型 | `backend-service/app/schemas/callback.py` | CallbackPayload, CallbackResponse |
| 模型评估 | `matlab-model/evaluate_objective_NSGA2.m` | `if nargout>1` 返回 results |
| 模型评估 | `matlab-model/evaluate_objective_PAEM.m` | 同上 |
| 模型评估 | `matlab-model/evaluate_objective.m` | 同上 |
| 前端接收 | `frontend-service/.../ProcessTransparentView.vue` | handleWsMessage + fetchProcessData |
| 前端 API | `frontend-service/src/api/index.ts` | postRun + getResults + getProcessData |
| 前端类型 | `frontend-service/src/types/process.ts` | ProcessDataResponse + SummaryMetrics |

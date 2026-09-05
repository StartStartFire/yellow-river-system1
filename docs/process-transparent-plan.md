# 过程透明化系统 — 分步实施计划

> 📋 **实施状态跟踪** — 本文档记录了过程透明化全链路的实施计划
>
> **前置条件**：核心开发（Step 1-6）已全部完成 ✅
> **当前状态**：
> - Phase E（MATLAB 改造）：✅ **已完成**
> - Phase F（后端改造）：✅ **已完成**
> - Phase G（前端改造）：✅ **已完成**（G2(c) 页面加载补拉 / G3 getProcessData 除外，见下）
>
> **实施与原计划的偏差**（以代码为准）：
> 1. E3/E4 的回调逻辑已抽取为独立文件 `push_callback_data.m` 统一封装（两个主循环调用它，内部再调 `http_callback_push`），并非在主循环内直接调用 `http_callback_push`
> 2. 过程数据年限由"最近 10 年"调整为**全部年份**（`push_callback_data.m` 中 `n_years = Y`），并新增 `start_year`、`coordination`、`constraint` 字段
> 3. 前端未实现 G2(c) 的 `GET /process` 页面加载补拉与 G3 的 `getProcessData`（`src/api/index.ts` 无此函数），过程透明页完全依赖 WS 实时推送

---

## 数据流架构

```
MATLAB 进化循环
  │  每代 write_json_log → JSONL 文件（每代写入，保持完整记录）
  │
  │  if 每 10 代:
  │
  ├─ http_callback_push('progress', summary_data)
  │   └─ POST /cb ─→ asyncio.Queue ─→ WebSocket ─→ 前端实时更新
  │     (汇总指标: best/avg/std/pareto_size + Pareto前沿目标值)
  │
  └─ http_callback_push('process_data', process_data)
      └─ POST /cb ─→ asyncio.Queue ─→ WebSocket ─→ 前端实时更新
        (也存储到 JobRecord，供 GET /process 补拉)
        (最优个体的水位/流量/出力过程，最近 10 年)

最终结果
  └─ write_json_log → JSONL
      ↓
  GET /results/{job_id} → 前端结果展示
```

---

## 阶段 E：MATLAB 改造（5 步）

### E1 改造三个 `evaluate_objective*.m` — 可选返回 `results`

> **目标**：给三个目标函数文件增加可选返回结果 `results`，用 `nargout` 控制，不影响原有调用。

#### E1.1 改造 `evaluate_objective.m`

- **文件**：`matlab-model/evaluate_objective.m`
- **改动**：

```matlab
% 函数签名（不变）
function X_F = evaluate_objective(x, V, M, Q_sediment)

% 在 X_F = [X_F, f_obj]; 之后、end 之前，新增：
if nargout > 1
    results = struct();
    results.Long.V = Vlong;
    results.Long.Qout = Qlongout;
    results.Liu.V = Vliu;
    results.Liu.Qout = Qliuout;
    results.N.Ntii_long = Ntii_long;
    results.N.Ntii_liu = Ntii_liu;
    results.N.Ntii_laxiwa = Ntii_laxiwa;
    results.N.Ntii_nina = Ntii_nina;
    results.N.Ntii_lijiaxia = Ntii_lijiaxia;
    results.N.Ntii_zhiganglaka = Ntii_zhiganglaka;
    results.N.Ntii_kangyang = Ntii_kangyang;
    results.N.Ntii_gongboxia = Ntii_gongboxia;
    results.N.Ntii_suzhi = Ntii_suzhi;
    results.N.Ntii_yanguoxia = Ntii_yanguoxia;
    results.N.Ntii_bapanxia = Ntii_bapanxia;
    results.N.Ntii_xiaoxia = Ntii_xiaoxia;
    results.N.Ntii_daxia = Ntii_daxia;
    results.N.Ntii_qingtongxia = Ntii_qingtongxia;
    results.N.Etii_longliu = Etii_longliu;    % 梯级总发电量（新增字段）
    results.liuzhou.Qshortage = Qshortage;     % 兰州缺水量
    results.liuzhou.T_Q_shortage = T_Q_shortage; % 全年总缺水量
    results.ecology.Qshortage_eco = Qshortage_eco; % 生态缺水量
    results.ecology.eco_rate = eco_rate;
    results.coordination.h_water = h_water;
    results.coordination.h_ele = h_ele;
    results.coordination.h_sed = h_sed;
    results.coordination.h_eco = h_eco;
end
```

#### E1.2 改造 `evaluate_objective_NSGA2.m`

- **文件**：`matlab-model/evaluate_objective_NSGA2.m`
- **改动**：

```matlab
% 函数签名
% 改前：
function X_F = evaluate_objective_NSGA2(x, V, M, Q_sediment, iteration_num)
% 改后：
function X_F = evaluate_objective_NSGA2(x, V, M, Q_sediment)
```

在 `X_F = [X_F, f_obj];` 之后、`end` 之前，新增与 E1.1 完全相同的 `if nargout > 1 ... end` 代码块。

#### E1.3 改造 `evaluate_objective_PAEM.m`

- **文件**：`matlab-model/evaluate_objective_PAEM.m`
- **改动**：

```matlab
% 函数签名
% 改前：
function X_F = evaluate_objective_PAEM(x, V, M, K_mut, accuracy, Q_sediment, iteration_num)
% 改后：
function X_F = evaluate_objective_PAEM(x, V, M, K_mut, accuracy, Q_sediment)
```

在 `X_F = [X_F, f_obj];` 之后、`end` 之前，新增与 E1.1 完全相同的 `if nargout > 1 ... end` 代码块。

#### 调用点同步更新

- **`nsga_2_para.m`** L59：
```matlab
% 改前：
offspring_all = [offspring_all; evaluate_objective_NSGA2(offspring_chromosome(j, 1: V) , V, M, Q_sediment, i)];
% 改后：
offspring_all = [offspring_all; evaluate_objective_NSGA2(offspring_chromosome(j, 1: V) , V, M, Q_sediment)];
```

- **`PAEM_para.m`** L69：
```matlab
% 改前：
offspring_all = [offspring_all; evaluate_objective_PAEM(offspring_chromosome(ii, 1:V), V, M, K_mut, accuracy, Q_sediment, i)];
% 改后：
offspring_all = [offspring_all; evaluate_objective_PAEM(offspring_chromosome(ii, 1:V), V, M, K_mut, accuracy, Q_sediment)];
```

---

### E2 新增 `find_representative_solution.m`

- **文件**：`matlab-model/find_representative_solution.m`
- **内容**：

```matlab
function best_idx = find_representative_solution(chromosome, pop, V, M)
% find_representative_solution - 从种群中选出代表性最优解
% 输入参数:
%   chromosome - 种群矩阵（pop × (V+M+2)），最后两列为 rank 和拥挤距离
%   pop        - 种群大小
%   V          - 决策变量维度
%   M          - 目标函数数量
% 输出参数:
%   best_idx   - 代表性个体的行索引
%
% 选出策略：Pareto 前沿（rank==1）中拥挤距离最大的个体

    rank_col = V + M + 1;
    crowd_col = V + M + 2;

    pareto_mask = (chromosome(:, rank_col) == 1);
    pareto_indices = find(pareto_mask);

    if isempty(pareto_indices)
        [~, best_idx] = max(chromosome(:, crowd_col));
        return;
    end

    if length(pareto_indices) == 1
        best_idx = pareto_indices(1);
        return;
    end

    pareto_crowd = chromosome(pareto_indices, crowd_col);
    [~, max_crowd_idx] = max(pareto_crowd);
    best_idx = pareto_indices(max_crowd_idx);
end
```

---

### E3 改造 `nsga_2_para.m` — 增强回调

- **文件**：`matlab-model/nsga_2_para.m`
- **改动**：将进化循环中第 84~94 行的日志和回调部分替换为：

```matlab
%% ========== 进度显示与日志记录 ==========
% 显示进度（每 5 代）
if ~mod(i, 5)
    clc
    fprintf('Running completed %d / %d \n', i, iterate);
end

% 记录日志（每代写入 JSONL，保持完整记录）
current_time = datestr(now, 'yyyy-mm-dd HH:MM:SS');
json_data = struct();
json_data.iteration = i;
json_data.timestamp = current_time;
json_data.objective_values = abs(chromosome(:, (V + 1): (V + M)));
json_data.progress_percent = round((double(i) / double(iterate)) * 100, 2);
write_json_log(json_data, json_fid);

% 每 10 代推送一次汇总指标 + 过程数据
if ~mod(i, 10) || i == iterate
    obj_values = abs(chromosome(:, (V + 1):(V + M)));

    % ===== 汇总指标（progress，走 WebSocket） =====
    summary_data = struct();
    summary_data.iteration = i;
    summary_data.timestamp = current_time;
    summary_data.progress_percent = json_data.progress_percent;
    summary_data.best_objectives = min(obj_values, [], 1);
    summary_data.avg_objectives = mean(obj_values, 1);
    summary_data.objective_std = std(obj_values, 0, 1);
    summary_data.pareto_size = sum(chromosome(:, V+M+1) == 1);

    pareto_mask = (chromosome(:, V+M+1) == 1);
    if any(pareto_mask)
        summary_data.pareto_objectives = obj_values(pareto_mask, :);
    else
        summary_data.pareto_objectives = [];
    end

    http_callback_push('progress', summary_data);

    % ===== 过程数据（process_data，WS + 后端存储） =====
    best_idx = find_representative_solution(chromosome, pop, V, M);
    best_x = chromosome(best_idx, 1:V);

    [~, results] = evaluate_objective_NSGA2(best_x, V, M, Q_sediment);

    n_years = min(10, Y);
    year_start = Y - n_years + 1;

    process_data = struct();
    process_data.iteration = i;
    process_data.timestamp = current_time;

    long_x = best_x(1:V/2);
    liu_x = best_x(V/2+1:V);
    sidx = (year_start - 1) * 20 + 1;
    eidx = Y * 20;

    process_data.longyang_level = long_x(sidx:eidx)';
    process_data.liujia_level = liu_x(sidx:eidx)';

    yr = year_start:Y;
    process_data.longyang_outflow = reshape(results.Long.Qout(yr, :)', 1, []);
    process_data.liujia_outflow = reshape(results.Liu.Qout(yr, :)', 1, []);
    process_data.longyang_power = reshape(results.N.Ntii_long(yr, :)', 1, []);
    process_data.liujia_power = reshape(results.N.Ntii_liu(yr, :)', 1, []);
    process_data.total_power = reshape(results.N.Etii_longliu(yr, :)', 1, []);
    process_data.water_shortage = reshape(results.liuzhou.Qshortage(yr, :)', 1, []);

    http_callback_push('process_data', process_data);
end
```

---

### E4 改造 `PAEM_para.m` — 同样增强回调

- **文件**：`matlab-model/PAEM_para.m`
- **改动**：与 E3 基本相同，差异如下：

```matlab
% 在回调中获取过程数据时调用 PAEM 版本：
[~, results] = evaluate_objective_PAEM(best_x, V, M, K_mut, accuracy, Q_sediment);
```

其余过程数据提取逻辑与 E3 完全一致（results 结构体字段相同）。

---

### E5 主循环中调用 evaluate 的参数更新

已在 E1 的"调用点同步更新"中覆盖，此处确认。

---

## 阶段 F：后端改造（4 步）

### F1 扩展 Pydantic 模型

- **文件**：`backend-service/app/schemas/callback.py`
- **改动**：

```python
class ProgressData(BaseModel):
    """type='progress' 时的 data 字段结构（汇总指标）"""
    iteration: int
    timestamp: str
    progress_percent: float
    best_objectives: list[float]
    avg_objectives: list[float]
    objective_std: list[float]
    pareto_size: int
    pareto_objectives: list[list[float]] | None = None


class ProcessDataPayload(BaseModel):
    """type='process_data' 时的 data 字段结构（过程数据）"""
    iteration: int
    timestamp: str
    longyang_level: list[float]
    liujia_level: list[float]
    longyang_outflow: list[float]
    liujia_outflow: list[float]
    longyang_power: list[float]
    liujia_power: list[float]
    total_power: list[float]
    water_shortage: list[float]
```

### F2 新增 JobRecord 过程数据存储

- **文件**：`backend-service/app/core/job_manager.py`
- **改动**：

```python
class JobRecord:
    def __init__(self, job_id: str, config: TaskConfig):
        self.job_id = job_id
        self.config = config
        self.status: str = "queued"
        self.progress_percent: float = 0.0
        self.created_at: str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.completed_at: str | None = None
        self.message: str | None = None
        self.result: TaskResult | None = None
        self.process_data: dict | None = None  # 最新过程数据
```

### F3 改造 `/cb` 端点 — 区分两种 type

- **文件**：`backend-service/app/api/callback.py`
- **改动**：

```python
@app.post("/cb", response_model=CallbackResponse)
async def callback(payload: CallbackPayload):
    """MATLAB 回调入口

    接收两种 type：
    - 'progress': 汇总指标 → WebSocket 实时推送
    - 'process_data': 过程数据 → WebSocket 推送 + 后端存储供补拉
    """
    cb_job_id = extract_job_id_from_data(payload.data)
    if not cb_job_id and job_manager:
        cb_job_id = job_manager.current_job_id

    if payload.type == 'progress':
        envelope = build_envelope(payload, job_id=cb_job_id)
        await callback_queue.put(envelope)

    elif payload.type == 'process_data':
        # 存储到后端供 GET /process 补拉
        if job_manager and cb_job_id:
            record = job_manager.get_status(cb_job_id)
            if record:
                record.process_data = payload.data
        # 同时推送到 WebSocket
        envelope = build_envelope(payload, job_id=cb_job_id)
        await callback_queue.put(envelope)

    else:
        logger.warning("未知回调类型: %s", payload.type)

    return CallbackResponse(received=True, job_id=cb_job_id)
```

### F4 新增 `GET /process/{job_id}` 端点

- **文件**：`backend-service/app/api/jobs.py`
- **新增端点**：

```python
@app.get("/process/{job_id}")
async def get_process_data(job_id: str):
    """获取最新过程数据

    当前端 WebSocket 连接较晚时，可通过此端点补拉最新过程数据。
    """
    if job_manager is None:
        raise HTTPException(status_code=503, detail="服务未就绪")

    record = job_manager.get_status(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"任务 {job_id} 不存在")

    return {
        "job_id": job_id,
        "status": record.status,
        "process_data": record.process_data,
        "message": None if record.process_data else "过程数据尚未生成",
    }
```

---

## 阶段 G：前端改造（3 步）

### G1 更新过程透明化类型定义

- **文件**：`frontend-service/src/types/process.ts`
- **新增**：

```typescript
export interface ProcessDataResponse {
  job_id: string
  status: string
  process_data: {
    iteration: number
    timestamp: string
    longyang_level: number[]
    liujia_level: number[]
    longyang_outflow: number[]
    liujia_outflow: number[]
    longyang_power: number[]
    liujia_power: number[]
    total_power: number[]
    water_shortage: number[]
  } | null
  message: string | null
}

export interface SummaryMetrics {
  iteration: number
  timestamp: string
  progress_percent: number
  best_objectives: number[]
  avg_objectives: number[]
  objective_std: number[]
  pareto_size: number
  pareto_objectives?: number[][]
}

export interface ConvergencePoint {
  iteration: number
  f1_min: number
  f2_min: number
  f3_min?: number
}
```

### G2 重写过程透明化页面数据逻辑

- **文件**：`frontend-service/src/views/process-transparent/ProcessTransparentView.vue`
- **改动要点**：

**a)** 新增响应式数据

```typescript
const convergenceHistory = ref<ConvergencePoint[]>([])
const paretoFront = ref<number[][]>([])
const processData = ref<ProcessDataResponse['process_data']>(null)
const dataReady = ref(false)
```

**b)** WebSocket 消息处理扩展

```typescript
const handleWsMessage = (msg: any) => {
  if (msg.type === 'progress' && msg.payload) {
    const d = msg.payload
    dataReady.value = true
    progress.value = d.progress_percent

    if (d.best_objectives) {
      convergenceHistory.value.push({
        iteration: d.iteration,
        f1_min: d.best_objectives[0] || 0,
        f2_min: d.best_objectives[1] || 0,
        f3_min: d.best_objectives[2],
      })
    }

    if (d.pareto_objectives) {
      paretoFront.value = d.pareto_objectives
    }

    if (d.progress_percent >= 100) {
      status.value = '已完成'
    }

    logIteration(d)
  }

  if (msg.type === 'process_data' && msg.payload) {
    processData.value = msg.payload
  }
}

const logIteration = (d: any) => {
  const now = new Date()
  const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
  const bestStr = d.best_objectives?.map((v: number) => v.toFixed(4)).join(', ') || ''
  const msg = `代 ${d.iteration}，最优: [${bestStr}]，前沿: ${d.pareto_size} 个`
  logsDisplay.value.unshift({ time, level: 'INFO', message: msg })
  if (logsDisplay.value.length > 100) logsDisplay.value = logsDisplay.value.slice(0, 100)
}
```

**c)** 页面加载时补拉过程数据

```typescript
onMounted(async () => {
  if (jobId.value) {
    try {
      const res = await fetch(`http://127.0.0.1:18080/process/${jobId.value}`)
      const data = await res.json()
      if (data.process_data) {
        processData.value = data.process_data
        dataReady.value = true
      }
    } catch { /* 静默 */ }
  }
  connectWebSocket()
})
```

**d)** 方案情景从 store 读取

```typescript
const planName = computed(() => {
  return store.dispatchScenario.scenarioName || `任务 ${jobId.value?.slice(0, 8)}`
})
```

**e)** ECharts option 替换数据源

```typescript
// 收敛曲线
const convergenceOption = computed(() => ({
  xAxis: { data: convergenceHistory.value.map(p => p.iteration) },
  series: [
    { name: '缺水量', data: convergenceHistory.value.map(p => p.f1_min) },
    { name: '发电量（负值）', data: convergenceHistory.value.map(p => p.f2_min) },
  ],
}))

// 水位曲线
const lyxLevelOption = computed(() => ({
  xAxis: { data: timeLabels(processData.value?.longyang_level?.length || 0) },
  series: [{ data: processData.value?.longyang_level || [] }],
}))
```

### G3 更新 API 客户端

- **文件**：`frontend-service/src/api/index.ts`
- **新增**：

```typescript
export async function getProcessData(jobId: string): Promise<ProcessDataResponse> {
  const res = await fetch(`${API_BASE}/process/${jobId}`)
  if (!res.ok) throw new Error(`获取过程数据失败 (${res.status})`)
  return res.json()
}
```

---

## 文件变更索引

| 阶段 | 文件 | 改动 | 说明 |
|------|------|------|------|
| E1.1 | `evaluate_objective.m` | 修改 | 末尾加 `if nargout>1` |
| E1.2 | `evaluate_objective_NSGA2.m` | 修改 | 删 `iteration_num` + 末尾加 results |
| E1.3 | `evaluate_objective_PAEM.m` | 修改 | 删 `iteration_num` + 末尾加 results |
| E2 | `find_representative_solution.m` | **新增** | 选拥挤度最大 Pareto 个体 |
| E3 | `nsga_2_para.m` | **重写回调** | 每 10 代推两种消息 |
| E4 | `PAEM_para.m` | **重写回调** | 同上 |
| E5 | `nsga_2_para.m` + `PAEM_para.m` | 修改 | 去掉 `i` 参数 |
| F1 | `backend-service/app/schemas/callback.py` | 修改 | 扩展 ProgressData，新增 ProcessDataPayload |
| F2 | `backend-service/app/core/job_manager.py` | 修改 | JobRecord 加 process_data |
| F3 | `backend-service/app/api/callback.py` | 修改 | /cb 区分两种 type |
| F4 | `backend-service/app/api/jobs.py` | **新增端点** | GET /process/{job_id} |
| G1 | `types/process.ts` | 修改 | 新增类型 |
| G2 | `ProcessTransparentView.vue` | **重写** | WS + 过程数据 + 收敛曲线 |
| G3 | `src/api/index.ts` | 修改 | 新增 getProcessData |

---

## 实施顺序

```
E1.1 → E1.2 → E1.3 → E2 → E3 → E4 → E5
  ↓
F1 → F2 → F3 → F4
  ↓
G1 → G2 → G3
```

**每步可验证**：
- E1.x：MATLAB 中 `[X_F, results] = evaluate_objective_NSGA2(...)` 能返回 results
- E2：MATLAB 中 `find_representative_solution(chromosome, ...)` 返回有效索引
- E3/E4：运行 `nsga_2_para(15, 5, 2, 1800, 0.9)` 观察推送日志
- F3：`curl POST /cb` 两种 type 分别验证
- F4：`curl GET /process/{job_id}` 返回过程数据
- G2：浏览器打开过程透明化页面，观察实时更新

---

## 关键设计决策

| 决策 | 方案 | 理由 |
|------|------|------|
| 推送频率 | 每 10 代 | 你确认 |
| 最优个体 | 拥挤度最大 Pareto 个体 | 问题 1 选 A |
| 过程数据年限 | 全部年份（`n_years = Y`，实施时由"最近 10 年"调整） | 实施调整 |
| 汇总指标传递 | WebSocket 实时推 | 你确认 |
| 过程数据传递 | WS 推送 + 后端存储供补拉 | 修复轮询延迟问题 |
| PAEM | 同样改造 | 问题 4 确认 |
| 消息类型分离 | 两种 type | 问题 5 确认 |
| JSONL 日志 | 保持每代写入 | 修复原文档错误 |
| `iteration_num` | 已移除 | 你确认 |
| `results` 获取 | `nargout>1` 直接改 evaluate | 修复新建重复文件问题 |
| 方案情景 | 从 store 读取 | 修复 Mock 场景问题 |

---

## 风险点

| 风险 | 说明 | 缓解 |
|------|------|------|
| `nargout>1` 开销 | 返回结构体拷贝 | MATLAB 写时复制，每 10 代一次无影响 |
| `Etii_longliu` 变量名 | 需确认拼写一致 | 已在 L500 确认 ✅ |
| `reshape` 列优先 | MATLAB `reshape` 按列 | 用 `reshape(A', 1, [])` 行优先 |
| 过程数据量 | ~10KB/次 | 可接受 |
| `process_data` 覆盖 | 只保留最新 | MVP 够用 |

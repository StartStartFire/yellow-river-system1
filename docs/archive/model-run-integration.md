# 模型运行对接 — 分步实施计划

> 📋 **实施状态跟踪** — 本文档记录了前后端联调的分步计划
>
> **前置条件**：核心开发（Step 1-6）已全部完成 ✅
> **当前状态**：
> - Phase A（前端改造）：大部分已完成
> - Phase B（MATLAB Pc参数化）：✅ **已完成**
> - Phase C（后端改造）：✅ **已完成**
> - Phase D（前后联调）：D1（POST /run 对接）、D2（WebSocket 对接）✅ **已完成**；D3 的结果查看未走 `GET /results`，实际由评价决策页的 `POST /evaluate` + `GET /decision/{job_id}` 实现

---

## 阶段划分

| 阶段 | 内容 | 涉及 | 前置 |
|------|------|------|------|
| **A** | 纯前端改造 — 类型/Mock/Store/视图 | `frontend-service/` | 无 |
| **B** | MATLAB 改造 — 使遗传算子参数可传入 | `matlab-model/` | 阶段 A 完成 |
| **C** | 后端改造 — 扩展 API、CORS、参数传递 | `backend-service/` | 阶段 A+B 完成 |
| **D** | 前后联调 — 配置汇总 → POST /run → 过程透明化 | 全部 | 阶段 A+B+C 完成 |

---

## 阶段 A：纯前端改造（8 大步）

### A1 更新类型定义

> **目标**：`types/model.ts` 中的类型与实际模型一致。

#### A1.1 更新算法参数类型

- **文件**：`frontend-service/src/types/model.ts`
- **改动**：`ModelAlgorithmState.parameters` 从 6 个字段改为 4 个

```typescript
// 改前
parameters: {
  populationSize: number
  iterationCount: number
  crossoverRate: number
  mutationRate: number    // ❌ 删除
  eliteRate: number       // ❌ 删除
  crowdingFactor: number  // ❌ 删除
}

// 改后
parameters: {
  populationSize: number   // 种群规模 → pop
  iterationCount: number   // 迭代次数 → iterate
  crossoverRate: number    // 交叉概率 Pc
  // kMut 不在此固定类型中，PAEM 切换时动态合并
}
```

#### A1.2 确认 `DispatchObjective` 可复用

当前已有 `id/name/description/icon` 字段，目标名改为"缺水量/发电量/协同度"即可复用，无需新增类型。

#### A1.3 确认结果目标名称

- `types/model.ts` 中无对应类型，`ResultResponse.objective_names` 仅在后端 `models.py` 中定义
- **无需前端改动**，后端返回什么前端展示什么

---

### A2 更新场景 Mock 数据

> **目标**：三大类场景均保留数据，但`multi-year → multi-objective`标记为`active`，其余标记`placeholder`。

#### A2.1 为子选项增加 `status` 字段

- **文件**：`mock/model-config/dispatchScenario.ts`
- **改动**：
  - 给 `DispatchSubOption` 类型增加 `status?: 'active' | 'placeholder'` 字段
  - `multi-year → multi-objective`：`status: 'active'`
  - 其他子选项（`flood`, `ice`, `supply` 等）：`status: 'placeholder'`

```typescript
{
  id: 'multi-year',
  name: '中长期调度',
  icon: 'calendar',
  description: '...',
  subOptions: [
    { 
      id: 'multi-objective', 
      name: '多目标优化调度', 
      description: '综合考虑防洪、发电、生态、供水等多目标协同优化',
      linkedObjectives: ['water-shortage', 'power-generation', 'coordination'],
      status: 'active',
    },
  ],
},
// critical-period 和 realtime 的子选项都加 status: 'placeholder'
```

#### A2.2 更新 `linkedObjectives`

- **改动**：`multi-objective` 的 `linkedObjectives` 改为 `['water-shortage', 'power-generation', 'coordination']`

---

### A3 更新调度主体 Mock 数据

> **目标**：数据保留完整，但视图层按场景过滤。场景为 `multi-objective` 时只显示龙+刘。

#### A3.1 保留完整水库数据

- **文件**：`mock/model-config/dispatchSubject.ts`
- **改动**：
  - `subjectReservoirGroups` **保留全部三个组合**（`long-liu`, `long-liu-hei`, `all`），但视图层根据场景过滤
  - 场景为 `multi-objective` 时只允许选择 `long-liu`

#### A3.2 更新场景→主体预填映射

- **改动**：
  - `scenarioToSubjectDefaults['multi-objective']`：
    - `reservoirIds: ['longyangxia', 'liujiaxia']`
    - `timeStep: '20时段/年'`
    - `scheduleFrequency: '无'`

#### A3.3 更新场景大类约束

- **改动**：
  - `scenarioCategoryConstraints['multi-year']`：
    - `allowedTimeSteps: ['20时段/年']`
    - `defaultTimeStep: '20时段/年'`
    - `maxDays: 365 * 54`（长系列）

---

### A4 更新模型算法 Mock 数据

> **目标**：保留全部四条模型数据条目，`stress` 标记为 `active`，其余 `placeholder`。

#### A4.1 更新模型列表

- **文件**：`mock/model-config/modelAlgorithm.ts`
- **改动**：
  - 给 `DispatchModel` 增加 `status?: 'active' | 'placeholder'` 字段
  - `dispatchModels.data`：

```typescript
[
  {
    id: 'stress',
    name: '多目标协同胁迫调度模型',
    supportedAlgorithms: ['nsga2', 'paem'],
    status: 'active',
  },
  // 以下占位保留
  { id: 'lro', name: '水库群优化调度模型', supportedAlgorithms: ['nsga2'], status: 'placeholder' },
  { id: 'multi_objective_dispatch', name: '多目标优化调度模型', supportedAlgorithms: ['paem'], status: 'placeholder' },
  { id: 'water_sediment_realtime', name: '水沙实时调度模型', supportedAlgorithms: ['nsga3'], status: 'placeholder' },
]
```

#### A4.2 更新算法列表

- **改动**：
  - 给 `OptimizationAlgorithm` 增加 `status?: 'active' | 'placeholder'` 字段
  - `optimizationAlgorithms.data`：

```typescript
[
  { id: 'nsga2', name: 'NSGA-II 多目标遗传算法', paramIds: ['populationSize', 'iterationCount', 'crossoverRate'], status: 'active' },
  { id: 'paem', name: 'PAEM 逐步逼近评价方法', paramIds: ['populationSize', 'iterationCount', 'crossoverRate', 'kMut'], status: 'active' },
  // 以下占位保留
  { id: 'pso', name: 'PSO 粒子群优化算法', paramIds: [], status: 'placeholder' },
  { id: 'nsga3', name: 'NSGA-III 多目标遗传算法', paramIds: [], status: 'placeholder' },
]
```

#### A4.3 重写目标列表

- **改动**：

```typescript
export const dispatchObjectives = {
  code: 200,
  message: 'success',
  data: [
    { id: 'water-shortage', name: '缺水量', description: '兰州断面多年平均缺水量最小化', icon: 'water' },
    { id: 'power-generation', name: '发电量', description: '梯级电站群年均发电量最大化', icon: 'flash' },
    { id: 'coordination', name: '协同度', description: '梯级调度系统总协同度最大化', icon: 'sync' },
  ] as DispatchObjective[],
}
```

#### A4.4 更新算法参数定义

- **改动**：`algorithmParameters.data` 只保留 4 个：

```typescript
[
  {
    id: 'populationSize', name: '种群规模',
    value: 200, min: 10, max: 1000, step: 10,
    description: '种群规模越大，搜索更充分，但计算耗时增加',
  },
  {
    id: 'iterationCount', name: '迭代次数',
    value: 500, min: 50, max: 2000, step: 50,
    description: '迭代次数越大，收敛更充分，但运行时间更长',
  },
  {
    id: 'crossoverRate', name: '交叉概率 Pc',
    value: 0.9, min: 0.5, max: 1.0, step: 0.01,
    description: '交叉概率越高，种群探索能力越强',
  },
  {
    id: 'kMut', name: '变异参数 K_mut',
    value: 50, min: 10, max: 200, step: 5,
    description: 'PAEM 算法专用变异参数，控制近似评价中的变异强度',
  },
]
```

#### A4.5 约束摘要

- **改动**：`constraintSummary.data.constraints` 保留数据但视图层暂时不展示

---

### A5 更新步骤间联动数据

> **目标**：联动映射以 `stress` 模型为核心。

#### A5.1 更新模型/算法中文名映射

- **文件**：`mock/model-config/linkage.ts`
- **改动**：

```typescript
export const modelLabelMap: ModelLabelMap = {
  stress: '多目标协同胁迫调度模型',
  lro: '水库群优化调度模型',
  multi_objective_dispatch: '多目标优化调度模型',
  water_sediment_realtime: '水沙实时调度模型（WSS）',
}

export const algorithmLabelMap: AlgorithmLabelMap = {
  nsga2: 'NSGA-II 多目标遗传算法',
  paem: 'PAEM 逐步逼近评价方法',
  pso: 'PSO 粒子群优化算法',
  nsga3: 'NSGA-III 多目标遗传算法',
}
```

#### A5.2 更新场景→模型兼容关系

```typescript
export const scenarioModelMap: ScenarioModelMap = {
  'multi-year': ['stress'],
  'critical-period': [],   // 暂无对应模型
  'realtime': [],          // 暂无对应模型
}

export const scenarioSubOptionModelMap: ScenarioSubOptionModelMap = {
  'multi-objective': 'stress',
}

export const reservoirGroupModelMap: ReservoirGroupModelMap = {
  'long-liu': ['stress'],
  'long-liu-hei': [],
  'all': [],
}
```

#### A5.3 更新目标→场景参数关联

```typescript
export const objectiveRelevantParams: ObjectiveRelevantParams = {
  'water-shortage': [],
  'power-generation': [],
  'coordination': [],
  // 西线调水和调沙流量是全局参数，不绑定具体目标
}
```

---

### A6 更新 Store 状态管理

> **目标**：默认值、联动逻辑、M 值映射与模型对齐。

#### A6.1 更新 step1State 默认联动

- **文件**：`stores/modelConfig.ts`
- **改动**：
  - `syncModelFromScenario`：当 `categoryId='multi-year'` 且 `subOptionId='multi-objective'` 时，强制 `selectedModel = 'stress'`
  - `syncObjectivesFromScenario`：联动目标为 `['water-shortage', 'power-generation']`（默认勾选前两个）
  - 新增 `syncSubjectFromScenario`：联动 Step 2 填充龙+刘

#### A6.2 新增 `syncSubjectFromScenario` 方法

```typescript
const syncSubjectFromScenario = (categoryId: string, subOptionId: string) => {
  if (categoryId === 'multi-year' && subOptionId === 'multi-objective') {
    step2State.value = {
      startTime: '1970-01',
      endTime: '2023-12',
      timeStep: '20时段/年',
      scheduleFrequency: '无',
      selectedReservoirIds: ['longyangxia', 'liujiaxia'],
      selectedGroupId: 'long-liu',
    }
  }
  // 其他场景暂不处理
}
```

#### A6.3 更新 step4State 默认值

```typescript
step4State = {
  selectedModel: 'stress',
  selectedAlgorithm: 'nsga2',
  selectedObjectives: ['water-shortage', 'power-generation'],  // 默认勾选前两个
  parameters: {
    populationSize: 200,
    iterationCount: 500,
    crossoverRate: 0.9,
    // mutationRate/eliteRate/crowdingFactor 已删除
  },
}
```

#### A6.4 新增 M 值计算

```typescript
/** 根据选中的目标数量计算 M 值（协同胁迫模型：2 个目标→M=2，3 个目标→M=3） */
const computedMValue = computed(() => {
  return step4State.value.selectedObjectives.length
})
```

**使用位置**：
- Step 4 视图：显示当前 M 值提示（"当前目标数：2 → M=2"）
- Step 6 视图：组装 `RunRequest` 时读取 `computedMValue.value` 作为 `M` 字段

#### A6.5 算法切换时 kMut 的处理

当用户切换算法时，Store 需要自动管理 `kMut` 参数的存在与否：

```typescript
const setModelAlgorithm = (data: Partial<typeof step4State.value>) => {
  Object.assign(step4State.value, data)
  // 切换到 PAEM 时确保 kMut 存在
  if (data.selectedAlgorithm === 'paem' && step4State.value.parameters.kMut === undefined) {
    step4State.value.parameters.kMut = 50
  }
  // 切换到 NSGA-II 时移除 kMut（干净移除）
  if (data.selectedAlgorithm === 'nsga2') {
    const { kMut, ...rest } = step4State.value.parameters
    step4State.value.parameters = rest
  }
}
```

#### A6.6 更新 `resetAll`

重置值时与上述默认值一致。

---

### A7 新增 HTTP 客户端层

> **目标**：为前端提供统一的 API 调用能力，配置 base URL、请求/响应拦截、错误处理。

#### A7.1 创建 API 模块

- **新增文件**：`frontend-service/src/api/index.ts`（或 `src/api/model.ts`）
- **内容**：

```typescript
const API_BASE = 'http://127.0.0.1:18080'

export async function postRun(config: RunRequestPayload): Promise<{ job_id: string }> {
  const res = await fetch(`${API_BASE}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || '提交运行失败')
  }
  return res.json()
}

export async function getResults(jobId: string): Promise<ResultResponse> {
  const res = await fetch(`${API_BASE}/results/${jobId}`)
  if (!res.ok) throw new Error('获取结果失败')
  return res.json()
}

// 补充类型定义
export interface RunRequestPayload {
  algorithm: string
  pop: number
  iterate: number
  M: number
  Q_sediment: number
  crossover_rate: number
  flag_xixian: string
  K_mut?: number  // PAEM 时传送
}
```

> 说明：系统集成阶段用 fetch 即可，暂不引入 axios。后续如需拦截器/超时/重试再替换。

#### A7.2 补充 `common.ts` 中的结果类型（可选）

```typescript
export interface ResultResponse {
  job_id: string
  status: string
  algorithm: string
  chromosome: (number | null)[][] | null
  objective_names: string[]
  message: string | null
  generated_at: string | null
}
```

---

### A8 更新视图层

> **目标**：UI 展示与模型对齐。

#### A8.1 Step 2 视图 — 调度主体

- **文件**：`views/model-config/dispatch-subject/DispatchSubjectView.vue`
- **改动**：
  - 当场景为 `multi-objective` 时：
    - 水库选择只显示龙羊峡+刘家峡，其他水库灰显不可选或隐藏
    - 时间步长显示"20时段/年"（只读文本，非下拉框）
    - 起止时间显示"1970-01 至 2023-12（长系列）"（只读文本）
    - 调度频率显示"无"（只读或下拉唯一选项）
  - 其他场景（`critical-period`/`realtime`）显示占位标记：`<el-tag type="info">待开放</el-tag>`

#### A8.2 Step 4 视图 — 模型算法

- **文件**：`views/model-config/model-algorithm/ModelAlgorithmView.vue`
- **需要确认**：原型页面使用哪些组件？以下为标准逻辑：

  - **模型选择**：
    - 遍历 `dispatchModels.data`，`status === 'active'` 的可选中，`placeholder` 的灰显+标签"待开放"
  - **算法选择**：
    - 遍历 `optimizationAlgorithms.data`，只显示当前模型 `supportedAlgorithms` 范围内的算法
    - 同理按 `status` 控制交互
  - **目标选择**：
    - 显示"缺水量/发电量/协同度"三个选项
    - 默认 `selectedObjectives` 从 store 读取（默认 `['water-shortage', 'power-generation']`）
    - 至少选 2 个，最多 3 个（可 UI 限制或后端校验）
  - **参数面板**：
    - NSGA-II：显示种群规模、迭代次数、交叉概率 3 个滑块
    - PAEM：显示种群规模、迭代次数、交叉概率、`K_mut` 4 个滑块
    - 每个滑块绑定到 `store.setAlgorithmParam(key, value)`
  - **约束面板**：
    - 暂时不展示，或显示 `<el-alert title="约束条件将在下一阶段开放" type="info" :closable="false" />`

#### A8.3 Step 5 视图 — 场景约束

- **文件**：`views/model-config/scenario-constraint/ScenarioConstraintView.vue`
- **改动**：
  - 只渲染 `westRoute` 和 `sedimentFlow` 两个配置项
  - 其余参数（`sedimentRequirement`, `ecologicalFlow`, `icePreventionFlow`）不渲染
  - 约束列表不渲染

#### A8.4 Step 6 视图 — 配置汇总 + 提交

- **文件**：`views/model-config/config-summary/ConfigSummaryView.vue`
- **改动**：

  **数据展示部分**：从 store 读取各步骤实际配置，展示汇总表：

  | 配置项 | 来源 Store 路径 | 示例值 |
  |-------|----------------|--------|
  | 调度场景 | `dispatchScenario.categoryId + subOptionId` | 中长期调度 → 多目标优化调度 |
  | 调度主体 | `dispatchSubject.selectedReservoirIds` | 龙羊峡 + 刘家峡 |
  | 调度时段 | `dispatchSubject.timeStep` | 20时段/年 |
  | 调度频率 | `dispatchSubject.scheduleFrequency` | 无 |
  | 调度模型 | `modelAlgorithm.selectedModel` → modelLabelMap | 多目标协同胁迫调度模型 |
  | 调度算法 | `modelAlgorithm.selectedAlgorithm` → algorithmLabelMap | NSGA-II |
  | 调度目标 | `modelAlgorithm.selectedObjectives` → 目标名 | 缺水量、发电量 |
  | M 值 | `computedMValue` | 2 |
  | 种群规模 | `modelAlgorithm.parameters.populationSize` | 200 |
  | 迭代次数 | `modelAlgorithm.parameters.iterationCount` | 500 |
  | 交叉概率 | `modelAlgorithm.parameters.crossoverRate` | 0.9 |
  | 变异参数 | `modelAlgorithm.parameters.kMut`（仅 PAEM） | 50 |
  | 西线调水 | `scenarioConstraint.params.westRoute` | 全无 |
  | 调沙流量 | `scenarioConstraint.params.sedimentFlow` | 1800 |

  **提交运行部分**：组装 `RunRequest`

  ```typescript
  // 值映射：westRoute → flag_xixian
  const westRouteMap: Record<string, string> = {
    none: '全无',
    upper: '有上无下',
    lower: '有下无上',
    all: '全有',
  }
  
  function assembleRunRequest(store: ReturnType<typeof useModelConfigStore>) {
    const payload: RunRequestPayload = {
      algorithm: store.modelAlgorithm.selectedAlgorithm,
      pop: store.modelAlgorithm.parameters.populationSize,
      iterate: store.modelAlgorithm.parameters.iterationCount,
      M: computedMValue.value,
      Q_sediment: parseFloat(store.scenarioConstraint.params.sedimentFlow),  // 字符串转数字
      crossover_rate: store.modelAlgorithm.parameters.crossoverRate,
      flag_xixian: westRouteMap[store.scenarioConstraint.params.westRoute] || '全无',
    }
    // PAEM 算法时附加 K_mut
    if (store.modelAlgorithm.selectedAlgorithm === 'paem') {
      payload.K_mut = store.modelAlgorithm.parameters.kMut
    }
    return payload
  }
  ```

  **提交逻辑**：
  1. 按钮点击 → `assembleRunRequest()` → `postRun()`
  2. 成功 → `router.push({ path: '/process-transparent', query: { job_id } })`
  3. 失败 → `ElMessage.error('提交失败: ' + error.message)`

#### A8.5 过程透明化页面 — 接收实时数据

- **文件**：`views/process-transparent/ProcessTransparentView.vue`
- **改动**：
  - 从 URL query 读取 `job_id`（`route.query.job_id`）
  - 连接 WebSocket：`new WebSocket('ws://127.0.0.1:18080/ws/' + jobId)`
  - 接收消息 → 更新进度条 / 迭代次数 / 目标值展示
  - 连接关闭/出错 → 显示提示
  - 提供"查看结果"按钮 → `router.push('/evaluation-decision?job_id=' + jobId)`

---

## 阶段 B：MATLAB 改造（4 步）

### B1 改造 genetic_operator.m

- **文件**：`matlab-model/genetic_operator.m`
- **改动**：

```matlab
% 函数签名
% 改前：
function f = genetic_operator(parent_chromosome, M, V, mu, mum, l_limit, u_limit)
% 改后：
function f = genetic_operator(parent_chromosome, M, V, mu, mum, l_limit, u_limit, Pc)

% 第 10 行
% 改前：
if rand(1) < 0.9
% 改后：
if rand(1) < Pc
```

### B2 改造 nsga_2_para.m

- **文件**：`matlab-model/nsga_2_para.m`
- **改动**：

```matlab
% 函数签名
% 改前：
function output = nsga_2_para(pop, iterate, M, Q_sediment)
% 改后：
function output = nsga_2_para(pop, iterate, M, Q_sediment, Pc)

% 第 53 行调用 genetic_operator 处
% 改前：
offspring_chromosome = genetic_operator(parent_chromosome, M, V, mu, mum, min_range, max_range);
% 改后：
offspring_chromosome = genetic_operator(parent_chromosome, M, V, mu, mum, min_range, max_range, Pc);
```

### B3 改造 PAEM_para.m

- **文件**：`matlab-model/PAEM_para.m`
- **改动**：

```matlab
% 函数签名
% 改前：
function output = PAEM_para(pop, iterate, K_mut, M, Q_sediment)
% 改后：
function output = PAEM_para(pop, iterate, K_mut, M, Q_sediment, Pc)

% 第 61 行调用 genetic_operator 处
% 改前：
offspring_chromosome = genetic_operator(parent_chromosome, M, V, mu, mum, min_range, max_range);
% 改后：
offspring_chromosome = genetic_operator(parent_chromosome, M, V, mu, mum, min_range, max_range, Pc);
```

### B4 更新 main.m（手动测试入口）

- **文件**：`matlab-model/main.m`
- **改动**：函数签名变化后，手动调用时需传 Pc 参数

```matlab
% 改前：
nsga_2_para(15, 20, 2, 1800.0)

% 改后：
nsga_2_para(15, 20, 2, 1800.0, 0.9)
```

---

## 阶段 C：后端改造（5 步）

### C0 新增 CORS 中间件

- **文件**：`backend-service/app/main.py`
- **改动**：在 `app = FastAPI(...)` 之后、路由定义之前插入：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],   # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### C1 扩展 RunRequest

- **文件**：`backend-service/app/schemas/job.py`
- **改动**：

```python
class RunRequest(BaseModel):
    algorithm: str = Field(default="nsga2", pattern=r"^(nsga2|paem)$")
    pop: int = Field(default=200, ge=1, description="种群大小")
    iterate: int = Field(default=500, ge=1, description="进化代数")
    M: int = Field(default=2, ge=1, description="目标函数个数")
    Q_sediment: float = Field(default=1800.0, ge=0.0, description="调沙流量")
    K_mut: int | None = Field(default=None, ge=0, description="PAEM 变异参数")
    crossover_rate: float = Field(default=0.9, ge=0.0, le=1.0, description="交叉概率 Pc")  # 新增
    flag_xixian: str = Field(default="全无", description="西线调水: 全无/全有/有上无下/有下无上")  # 新增
```

**重要**：后端默认值保持较小值（方便 curl / 直接测试），前端提交时用自己的大值：

```python
pop: int = Field(default=15, ge=1, description="种群大小")       # 后端测试用小值
iterate: int = Field(default=20, ge=1, description="进化代数")   # 后端测试用小值
```

前端组装时覆盖这些默认值（前端默认 pop=200, iterate=500）。

### C2 扩展 TaskConfig

- **文件**：`backend-service/app/core/executor.py`
- **改动**：

```python
@dataclass
class TaskConfig:
    algorithm: str
    pop: int
    iterate: int
    M: int
    Q_sediment: float
    K_mut: int | None = None
    crossover_rate: float = 0.9    # 新增
    flag_xixian: str = "全无"       # 新增
    job_id: str = ""
```

### C3 扩展 MatlabExecutor

- **文件**：`backend-service/app/services/matlab.py`

#### C3.1 改造 `_run_optimization_sync`

```python
def _run_optimization_sync(self, task: TaskConfig) -> list:
    # 根据西线调水参数重新加载数据（每次运行前确保数据状态正确）
    self._eng.load_data(self._cfg.data_file, task.flag_xixian, nargout=0)

    if task.algorithm == "nsga2":
        result = self._eng.nsga_2_para(
            float(task.pop),
            float(task.iterate),
            float(task.M),
            float(task.Q_sediment),
            float(task.crossover_rate),  # 新增 Pc 参数
            nargout=1,
        )
    elif task.algorithm == "paem":
        if task.K_mut is None:
            raise ValueError("PAEM 算法需要提供 K_mut 参数")
        result = self._eng.PAEM_para(
            float(task.pop),
            float(task.iterate),
            float(task.K_mut),
            float(task.M),
            float(task.Q_sediment),
            float(task.crossover_rate),  # 新增 Pc 参数
            nargout=1,
        )
    else:
        raise ValueError(f"不支持的算法: {task.algorithm}")

    return self._extract_chromosome(result)
```

#### C3.2 `_start_engine_sync` 使用默认 `flag_xixian`

```python
def _start_engine_sync(self):
    self._eng = matlab.engine.start_matlab()
    self._eng.cd(self._cfg.matlab_root)
    # 启动时用默认 '全无' 加载，运行时再按任务参数重载
    self._eng.load_data(self._cfg.data_file, '全无', nargout=0)
```

### C4 删除 config.py 中硬编码的 `flag_xixian`

- **文件**：`backend-service/app/config.py`
- **改动**：删除 `flag_xixian: str = "全无"` 行
- **保留**：`data_file`、`matlab_root` 等路径配置不变

### C5 更新 objective_names

- **文件**：`backend-service/app/schemas/result.py`
- **改动**：`ResultResponse` 的 `objective_names` 按 M 值动态返回：

```python
class ResultResponse(BaseModel):
    job_id: str
    status: str
    algorithm: str
    chromosome: list[list[float | None]] | None = None
    objective_names: list[str] = ["缺水量", "发电量", "协同度"]
    message: str | None = None
    generated_at: str | None = None

    @field_serializer('objective_names')
    def serialize_objective_names(self, v):
        # 从 chromosome 列数推断实际的 objective_names
        if self.chromosome and len(self.chromosome) > 0:
            # chromosome 结构: [V个决策变量, M个目标值, rank, crowding_distance]
            # 从总列数 - V - 2 推断 M
            # 但更简单：直接使用当前任务配置的 M 值
            pass  # 方案见下方
```

**简化方案**：前端 Store 已经知道 M 值和目标名，后端返回固定 3 个目标名，前端按 M 值截取展示即可。

> 或者更简单：保持 `objective_names` 固定为 `["缺水量", "发电量", "协同度"]`，前端根据 `M` 值只显示前 `M` 个。

---

## 阶段 D：前后联调（3 步）

### D1 POST /run 接口对接

- 前端 A8.4 中实现的提交逻辑
- curl 验证（后端默认小参数快速测试）：

```bash
curl -X POST http://127.0.0.1:18080/run \
  -H "Content-Type: application/json" \
  -d '{"algorithm":"nsga2","pop":15,"iterate":20,"M":2,"Q_sediment":1800,"crossover_rate":0.9,"flag_xixian":"全无"}'
```

### D2 WebSocket 实时进度对接

- 前端 A8.5 中实现的 WebSocket 客户端
- curl 验证（先开一个终端跑 WebSocket，再提交任务）：

```bash
# 终端 1：连接 WebSocket（需要 wscat 工具）
wscat -c ws://127.0.0.1:18080/ws/test-job-id

# 终端 2：提交任务
curl -X POST http://127.0.0.1:18080/run ...
```

### D3 结果查看

- 前端调用 `GET /results/{job_id}`
- 展示 Pareto 前沿数据（可根据染色体矩阵绘制散点图）

---

## 文件变更索引（总览）

| 阶段 | 文件 | 改动类型 | 简要说明 |
|------|------|---------|---------|
| A1 | `types/model.ts` | 修改 | 删除 mutationRate/eliteRate/crowdingFactor |
| A2 | `mock/model-config/dispatchScenario.ts` | 修改 | 增加 status 字段，精简 multi-year 子选项 |
| A3 | `mock/model-config/dispatchSubject.ts` | 修改 | 更新预填映射，保留完整数据 |
| A4 | `mock/model-config/modelAlgorithm.ts` | **重写** | 模型/算法/目标/参数全部对齐 |
| A5 | `mock/model-config/linkage.ts` | **重写** | 联动关系以 stress 为核心 |
| A6 | `stores/modelConfig.ts` | **重写关键部分** | 默认值、联动逻辑、M值、kMut切换 |
| A7.1 | `src/api/index.ts` | **新增** | HTTP 客户端（fetch 封装） |
| A7.2 | `types/common.ts` | 修改 | 新增 ResultResponse 类型 |
| A8.1 | `views/.../dispatch-subject/` | 修改 | 只读显示时间/时段/频率 |
| A8.2 | `views/.../model-algorithm/` | 修改 | 精简 UI，status 控制交互 |
| A8.3 | `views/.../scenario-constraint/` | 修改 | 只保留西线+调沙 |
| A8.4 | `views/.../config-summary/` | **重写** | 真实数据 + 提交按钮 + 错误处理 |
| A8.5 | `views/.../process-transparent/` | 修改 | WebSocket 实时对接 |
| B1 | `matlab-model/genetic_operator.m` | 修改 | Pc 从硬编码 0.9 改为函数参数 |
| B2 | `matlab-model/nsga_2_para.m` | 修改 | 函数签名增加 Pc，下传 |
| B3 | `matlab-model/PAEM_para.m` | 修改 | 函数签名增加 Pc，下传 |
| B4 | `matlab-model/main.m` | 修改 | 手动测试入口同步新签名 |
| C0 | `backend-service/app/main.py` | 修改 | 新增 CORS 中间件 |
| C1 | `backend-service/app/schemas/job.py` | 修改 | RunRequest 加 crossover_rate/flag_xixian |
| C2 | `backend-service/app/core/executor.py` | 修改 | TaskConfig 加 crossover_rate/flag_xixian |
| C3 | `backend-service/app/services/matlab.py` | **重写关键部分** | 参数传递 + flag_xixian 动态加载 |
| C4 | `backend-service/app/config.py` | 修改 | 删除硬编码 flag_xixian |
| C5 | `backend-service/app/schemas/result.py` | 修改 | objective_names 动态化 |

---

## 实施顺序建议

```
Phase A1 → A2 → A3 → A4 → A5 → A6 → A7 → A8.1~A8.5
  （前端可独立运行，Mock 数据验证 UI）

       ↓ 全部完成后

Phase B1 → B2 → B3 → B4
  （MATLAB 改造，在 MATLAB CLI 中手动测试验证）

       ↓ 全部完成后

Phase C0 → C1 → C2 → C3 → C4
  （后端改造，用 curl 测试验证）

       ↓ 全部完成后

Phase D1 → D2 → D3
  （端到端联调）
```

**每步完成后验证**：

| 阶段 | 验证方法 |
|------|---------|
| A | 浏览器访问 `localhost:3000`，检查 UI 显示、选项过滤、默认值 |
| B | MATLAB 命令行调用 `nsga_2_para(15, 20, 2, 1800.0, 0.9)` 不报错 |
| C | `curl POST /run` 返回 job_id，状态为 running |
| D | 前端提交 → 后端执行 → WS 收到进度 → 结果可查 |

---

## 风险点

| 风险 | 说明 | 缓解措施 |
|------|------|---------|
| `flag_xixian` 动态重载 | MATLAB 中每次 `_run_optimization_sync` 都调用 `load_data` 覆盖全局变量 | 确保只在优化开始前调用一次，不在进化循环中调用 |
| MATLAB 参数顺序变化 | 修改函数签名后，Python 调用参数顺序需同步 | 修改后先在 MATLAB 命令行手动测试新签名 |
| ~~过程透明化页面尚无真实 WebSocket 逻辑~~ | 已解决：ProcessTransparentView 已接入 `ws://<host>:18080/ws/{job_id}` | — |
| `genetic_operator.m` 被两个主循环共享 | B1 修改后需确保 NSGA-II 和 PAEM 都正确传入 Pc | B2/B3 同时检查调用点 |
| ~~前端无 HTTP 客户端~~ | 已解决：`src/api/index.ts` 已存在（fetch 封装，base URL 按 hostname 动态拼接） | — |
| CORS 跨域 | 已解决：后端 CORS 默认 `["*"]`（内网调试用） | 上线前收紧为前端地址白名单 |
| 前端提交类型转换 | `sedimentFlow` 是字符串，需转 number | A8.4 映射表中用 `parseFloat()` |
| 提交失败时无反馈 | 后端未启动 / 网络超时 / 校验失败 | A8.4 中 `try-catch` + `ElMessage.error` |

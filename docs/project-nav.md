# 项目目录导航

> 快速了解 `matlab-model/`（MATLAB 模型）、`backend-service/`（Python Web 服务）、`evaluation-model/`（评价系统）、`frontend-service/`（Vue3 前端）四个目录的结构与职责。
> 本文档为 AI 和开发者设计，帮助在不逐个读取文件的前提下迅速定位代码。

---

## 一、总览

```
E:\model\yellow_river_project\
├── matlab-model/                     # MATLAB 多目标优化调度模型
│   ├── nsga_2_para.m          # NSGA-II 主循环（入口）
│   ├── PAEM_para.m            # PAEM 主循环（入口）
│   ├── evaluate_objective*.m  # 4 个评价函数（含 save_info 版本）
│   ├── *.m                    # 15 个辅助函数
│   ├── data.xlsx              # 输入数据（18 个 sheet）
│   ├── push_callback_data.m   # 回调数据统一封装（每 10 代推 progress + process_data）
│   ├── http_callback_push.m    # HTTP 回调推送（webwrite POST）
│   └── docs/                  # 专属文档
│       ├── model-specification.md
│       ├── scheduling-rules.md
│       └── project-analysis.md
│
├── backend-service/               # Python FastAPI Web 服务
│   ├── run.py                 # 启动脚本
│   ├── requirements.txt       # 依赖
│   ├── app/                   # 四层架构
│   │   ├── api/               # 5 个路由模块
│   │   ├── core/              # 4 个业务核心模块
│   │   ├── schemas/           # 4 个 Pydantic 模型文件
│   │   └── services/          # MATLAB Engine 封装
│   └── docs/                  # 专属文档
│       ├── api-reference.md
│       └── backend-architecture.md
│
├── evaluation-model/                # Python 评价系统（独立模块）
│   ├── evaluation_system/     # NMF/PP/AHP_FUZZY + 整合
│   └── docs/                  # 专属文档
│       └── evaluation-data-specification.md
│
├── frontend-service/      # Vue3 + TypeScript 前端（独立项目）
│   ├── index.html
│   ├── vite.config.ts         # 构建配置
│   ├── package.json
│   └── src/
│       ├── main.ts            # 入口
│       ├── App.vue
│       ├── router/            # 路由（13 个视图）
│       ├── stores/            # Pinia 状态管理
│       ├── types/             # TypeScript 类型定义
│       ├── mock/              # Mock 数据（部分页面；过程透明/评价决策/配置汇总已接真实 API，见 §5.5）
│       ├── views/             # 13 个页面视图
│       ├── components/        # 35+ 组件
│       └── layouts/           # 布局组件
│
├── docs/                      # 跨项目文档
│   ├── project-nav.md         # ← 本文档（项目目录导航）
│   ├── work-log.md            # AI 工作日志
│   ├── model-run-integration.md   # ⬜ 模型运行对接方案
│   ├── process-transparent-plan.md # ⬜ 过程透明化方案
│   ├── data-flow.md           # ⬜ 全过程数据流向（目标设计）
│   │
│   └── 子项目专属文档见各自 directory/docs/
│
├── _sandbox/                   # 临时测试脚本（AI 调试用，已 gitignore）
├── CLAUDE.md                  # 项目开发规范（已同步最新结构）
```

---

## 二、MATLAB 模型 (`matlab-model/`)

### 2.1 主要文件

MATLAB 模型共 23 个 `.m` 文件，核心文件如下（完整列表见目录树上方）：

| 类别 | 文件 | 说明 |
|------|------|------|
| 入口 | `nsga_2_para.m`, `PAEM_para.m` | NSGA-II / PAEM 主循环，直接由 Python 后端调用 |
| 数据 | `load_data.m`, `data.xlsx` | 加载 Excel 数据 → 全局变量 |
| 评价 | `evaluate_objective*.m` (4个) | 目标函数评估：基础版、NSGA2版、PAEM版、带过程数据版 |
| 遗传 | `initialize_population.m`, `genetic_operator.m`, `tournament_selection.m`, `replace_chromosome.m`, `non_domination_sort_mod.m` | 种群初始化、SBX交叉+多项式变异、锦标赛选择、精英替换、非支配排序 |
| 工具 | `chz1.m`, `chz2.m`, `mutation_one_variable.m`, `find_nondominated_solution.m`, `find_representative_solution.m` | 插值、PAEM变异、非支配解提取、代表性解选择 |
| 日志 | `write_json_log.m`, `init_log_file.m`, `preprocess_results_for_json.m` | JSONL 文件写入和管理 |
| 回调 | `push_callback_data.m`, `http_callback_push.m` | 回调数据统一封装（汇总指标 + 过程数据）、HTTP POST 推送到 Web 服务 |

### 2.2 数据流

```
load_data.m → 全局变量 (Y, VarMin, VarMax, LONG_IN, …)
     ↓
nsga_2_para.m / PAEM_para.m
     ↓
initialize_population.m → evaluate_objective*.m → non_domination_sort_mod.m
     ↓  (迭代 iterate 次)
tournament_selection.m → genetic_operator.m → evaluate_objective*.m
     ↓
non_domination_sort_mod.m → replace_chromosome.m
     ↓  (每代)
write_json_log.m → NSGA2_progress.jsonl / PAEM_progress.json
push_callback_data.m → http_callback_push.m → POST → Web 服务 /cb
     ↓
结果 → output.chromosome / evaluating / plan_details（PAEM: chromosome_acc）
```

### 2.3 核心参数

| 参数 | 位置 | 说明 | 当前值 |
|------|------|------|--------|
| `pop` | 函数入参 | 种群大小 | 默认 15 |
| `iterate` | 函数入参 | 进化代数 | 默认 20 |
| `M` | 函数入参 | 目标函数数 | 默认 2 |
| `Q_sediment` | 函数入参 | 调沙流量 | 默认 1800 |
| `K_mut` | PAEM 入参 | PAEM 变异参数 | 默认 50 |
| `mu` | `nsga_2_para.m` L49 | SBX 交叉分布指数 | **硬编码 20** |
| `mum` | `nsga_2_para.m` L50 | 多项式变异分布指数 | **硬编码 20** |
| `Pc` | `genetic_operator.m` L10 | 交叉概率 | **硬编码 0.9** |
| `pool` | `nsga_2_para.m` L42 | 交配池大小 | `fix(pop/2)` |
| `tour` | `nsga_2_para.m` L43 | 锦标赛规模 | **硬编码 2** |
| `Y` | `load_data.m` L33 | 年数（数据决定） | 54（1970-2023） |
| `nVar` | `nsga_2_para.m` L25 | 决策变量维度 | `20 × Y × 2 = 2160` |
| 起调水位 | `evaluate_objective*.m` L21-22 | 龙羊峡/刘家峡 | **硬编码 2580/1720** |
| 防凌流量 | `evaluate_objective_NSGA2.m` L29 | 11月~3月 | **硬编码 [610,420,420,420,420]** |

### 2.4 数据文件

- **`data.xlsx`** — 18 个 sheet，包含 54 年（1970-2023）实测数据
  - 水位-流量/库容曲线：`LONG-ZQ`, `LONG-ZV`, `LIU-ZQ`, `LIU-ZV`
  - 入流/区间：`LONGIN`, `LONG-LIU`, `LIU-LAN`
  - 用水/调水：`longliu_water`, `liulan_water`, `xixian_up`, `xixian_down`
  - 需水：`LAN`, `LAN-unagr`, `LAN-agr`
  - 生态/频率：`Q_eco`, `P`
  - 水位边界：`LONGLIU-BOUND`
  - 物理参数：`CANSHU`

### 2.5 重要约束（目标函数内）

| 约束 | 实现位置 | 处理方式 |
|------|----------|----------|
| 水量平衡 | `evaluate_objective*.m` | 物理方程强制 |
| 库容边界 | VarMin/VarMax 截断 | 遗传算子 + 评估内修正 |
| 装机容量 | 龙羊峡 128 万kW / 刘家峡 122.5 万kW | 截断 |
| 保证出力 | 龙羊峡 58.7 / 刘家峡 40 万kW | 迭代增大出库 |
| 生态流量 | 出库 350~1050 m³/s | 强制修正 |
| 兰州断面需水 | Qliuout ≥ LAN - LIU_LAN | 强制抬升 |
| 调沙规则 | 7月下旬-8月上旬，P≤0.80 | 规则驱动 |

---

## 三、Python Web 服务 (`backend-service/`)

### 3.1 文件清单与职责

| 文件 | 职责 | 关键细节 |
|------|------|----------|
| `run.py` | 启动入口 | `uvicorn.run("app.main:app", host, port)` |
| `requirements.txt` | 依赖 | fastapi, uvicorn, pydantic, matlabengine（R2024a） |
| `app/config.py` | **全局配置单例** | `Config` dataclass：服务器、MATLAB路径、回调地址、CORS、默认参数 |
| `app/main.py` | **FastAPI 入口** | lifespan 生命周期；5 个路由模块注册 |
| `app/api/health.py` | **健康检查** | GET /health |
| `app/api/jobs.py` | **任务 CRUD** | POST /run, GET /status, /jobs, /results, /process |
| `app/api/evaluate.py` | **评价排名** | POST /evaluate, GET /evaluate/{job_id} |
| `app/api/ws.py` | **WebSocket** | WS /ws/{job_id} |
| `app/api/callback.py` | **回调接收** | POST /cb |
| `app/core/executor.py` | **执行器抽象** | `BaseExecutor` ABC + `TaskConfig`/`TaskResult` dataclass |
| `app/core/job_manager.py` | **任务队列管理** | `JobManager`：asyncio.Queue 串行化，状态机 queued→running→completed/failed |
| `app/core/callback.py` | **回调消息缓冲** | `CallbackQueue`（asyncio.Queue 封装） |
| `app/core/websocket.py` | **WebSocket 广播** | `ConnectionManager`（按 job_id 分组）+ `broadcast_loop()` 后台消费 |
| `app/schemas/job.py` | **任务模型** | RunRequest（含约束参数）、JobStatusResponse、JobSummary |
| `app/schemas/evaluate.py` | **评价模型** | EvaluateRequest、EvaluateResponse |
| `app/schemas/result.py` | **结果模型** | ResultResponse（chromosome + evaluating 双矩阵） |
| `app/schemas/callback.py` | **回调模型** | CallbackPayload、CallbackResponse |
| `app/services/matlab.py` | **MATLAB Engine 封装** | MatlabExecutor：单线程串行化，约束参数动态注入 |

### 3.2 API 端点

完整 API 文档见 `backend-service/docs/api-reference.md`，所有端点汇总如下：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/run` | 提交优化任务 |
| GET | `/status/{job_id}` | 查询任务状态 |
| GET | `/jobs` | 任务列表 |
| GET | `/results/{job_id}` | 获取 Pareto 解集 |
| GET | `/process/{job_id}` | 补拉过程数据 |
| POST | `/evaluate` | 运行评价算法 |
| GET | `/evaluate/{job_id}` | 获取评价缓存 |
| GET | `/decision/{job_id}` | 决策方案明细（前 10 个方案） |
| POST | `/cb` | MATLAB 回调接收 |
| WS | `/ws/{job_id}` | 实时订阅 |

### 3.3 通信链路

```
MATLAB (nsga_2_para.m / PAEM_para.m)
  │ 每 10 代（含最后一代）调用 push_callback_data.m
  │ （内部经 http_callback_push.m → webwrite POST → http://127.0.0.1:18080/cb）
  ▼
FastAPI /cb 端点
  │ Pydantic 校验 → asyncio.Queue
  ▼
broadcast_loop 后台协程
  │ 按 job_id 分发
  ▼
WebSocket /ws/{job_id} → 前端实时更新
```

### 3.4 当前配置（config.py 默认值）

```
host: 0.0.0.0                        # 监听所有网卡（本机访问 127.0.0.1:18080）
port: 18080
cors_origins: ["*"]                  # 系统集成阶段允许所有来源，内网调试用
matlab_root: <项目根>/matlab-model    # 自动基于项目根目录计算（property），换机器无需修改
data_file: data.xlsx
callback_host: 127.0.0.1             # MATLAB 回调地址（写死在 http_callback_push.m）
callback_port: 18080
callback_timeout: 1.0s
default_pop: 15
default_iterate: 20
default_m: 2
default_q_sediment: 1800.0
default_k_mut: 50
```

---

## 四、Python 评价系统（`evaluation-model/`）

### 4.1 文件清单与职责

| 文件 | 职责 | 关键细节 |
|------|------|----------|
| `evaluation_system/__init__.py` | **统一入口** | `run_complete_evaluation(data_source, config_dict)` 一键运行 3 种算法 + 整合（另有 `run_single_algorithm` 等导出） |
| `evaluation_system/main_controller.py` | **主控制器** | `MainController`：单算法运行、全算法并行、排名整合、总结报告 |
| `evaluation_system/unified_config.py` | **统一配置管理器** | 聚合 NMF/PP/AHP_FUZZY 三种算法的配置参数 |
| `evaluation_system/unified_output.py` | **统一输出处理器** | 输出标准化，生成排名/收敛曲线/雷达图/子系统得分 |
| `evaluation_system/algorithm_base.py` | **算法基类** | 定义 AlgorithmBase 公共接口 |
| `evaluation_system/nmf_algorithm.py` | **NMF 算法** | 非负矩阵分解布谷鸟搜索，输出权向量 H（越大越优） |
| `evaluation_system/pp_algorithm.py` | **PP 算法** | 投影寻踪布谷鸟搜索，输出投影值 z（越大越优） |
| `evaluation_system/fuzzy_algorithm.py` | **AHP 模糊综合评价** | 5 子系统先独立评 + AHP 再综合，输出最终得分 |
| `evaluation_system/rank_sum_theory.py` | **序号总和整合** | 将 NMF/PP/AHP_FUZZY 三种排名整合为最终排名 |
| `evaluation_system/standardization_algorithm.py` | **标准化** | 评价指标标准化处理 |
| `evaluation_system/standardization_main.py` | **标准化主控** | 标准化流程调度 |

### 4.2 评价系统调用流程

```
POST /evaluate → evaluate.py
  → run_complete_evaluation(data_source=矩阵, config_dict=配置)
    → NMFAlgorithm.run()       → W, H, ranks, cost_history
    → PPAlgorithm.run()        → a, z, ranks, cost_history
    → FuzzyAlgorithm.run()     → final_scores, ranks, ahp_weights, 一级评价
    → RankSumTheory.integrate() → final_ranking (序号总和)
    → _build_evaluation_cache() → rankings + convergence + radar + raw_indicators
```

---

## 五、Vue3 前端 (`frontend-service/`)

### 5.1 目录结构

```
src/
├── main.ts                     # App 入口
├── App.vue                     # 根组件 → MainLayout
├── router/index.ts             # 13 个路由
├── stores/
│   ├── app.ts                  # 全局应用状态
│   └── modelConfig.ts          # 模型配置 6 步流程状态（核心）
├── types/
│   ├── model.ts                # 模型配置相关类型（核心）
│   ├── reservoir.ts            # 水库相关类型
│   ├── common.ts               # 通用类型（ApiResponse 等）
│   ├── process.ts              # 过程透明化类型
│   ├── evaluation.ts           # 评价决策类型
│   ├── caseLibrary.ts          # 案例库类型
│   └── reportStatistics.ts     # 报表统计类型
├── mock/                       # Mock 数据（部分页面仍在用；评价决策/过程透明/配置汇总已接真实 API）
│   ├── model-config/           # 6 步流程的 Mock
│   │   ├── dispatchScenario.ts
│   │   ├── dispatchSubject.ts
│   │   ├── modelData.ts
│   │   ├── modelAlgorithm.ts
│   │   ├── scenarioConstraint.ts
│   │   └── linkage.ts          # 步骤间联动关系
│   ├── basicData.ts
│   ├── home.ts
│   ├── waterCondition.ts
│   ├── evaluationDecision.ts
│   ├── caseLibrary.ts
│   └── reportStatistics.ts
├── views/                      # 13 个页面视图
│   ├── home/HomeView.vue
│   ├── basic-data/BasicDataView.vue
│   ├── water-condition/WaterConditionView.vue
│   ├── model-config/           # 模型配置 6 步流程（核心功能）
│   │   ├── dispatch-scenario/  # Step 1: 调度场景
│   │   ├── dispatch-subject/   # Step 2: 调度主体
│   │   ├── model-data/         # Step 3: 调度数据
│   │   ├── model-algorithm/    # Step 4: 模型算法
│   │   ├── scenario-constraint/# Step 5: 场景约束
│   │   └── config-summary/     # Step 6: 配置汇总
│   ├── process-transparent/ProcessTransparentView.vue
│   ├── evaluation-decision/EvaluationDecisionView.vue
│   ├── case-library/CaseLibraryView.vue
│   └── report-statistics/ReportStatisticsView.vue
├── components/                 # 35+ 组件（按页面分组）
│   ├── common/                 # PanelCard, StatusTag
│   ├── chart/                  # BaseChart, ReservoirSectionGraph
│   ├── home/                   # 首页组件群
│   ├── basic-data/             # 基础数据组件群
│   ├── model-config/           # 模型配置组件群
│   │   ├── ModelConfigStepBar.vue
│   │   ├── ModelConfigFooter.vue
│   │   ├── model-data/         # 模型数据组件
│   │   ├── model-algorithm/    # 算法参数、约束面板
│   │   ├── dispatch-scenario/  # 场景卡片
│   │   ├── config-summary/     # 配置确认、方案表
│   │   └── common/             # ConfirmActionDialog
│   ├── evaluation-decision/    # 评价决策组件群
│   └── case-library/           # 案例库组件群
└── layouts/MainLayout.vue      # 主布局
```

### 5.2 模型配置 6 步流程（核心功能）

| 步骤 | 视图 | 关键状态 | 数据来源 |
|------|------|----------|----------|
| **Step 1: 调度场景** | `dispatch-scenario/` | `categoryId`, `subOptionId`, `scenarioName` | Mock (3 大类 9 子类) |
| **Step 2: 调度主体** | `dispatch-subject/` | `startTime`, `endTime`, `timeStep`, `selectedReservoirIds` | Mock (13 水库, 3 预设组合) |
| **Step 3: 调度数据** | `model-data/` | `activeMenuId`, `dateRange`, `selectedDataIds` | Mock (曲线/表格展示) |
| **Step 4: 模型算法** | `model-algorithm/` | `selectedModel`, `selectedAlgorithm`, `parameters`, `selectedObjectives` | Mock (4 模型, 4 算法, 12 参数) |
| **Step 5: 场景约束** | `scenario-constraint/` | `scenarioType`, `params` (西线/调沙/生态/防凌) | Mock (5 配置项, 8 约束) |
| **Step 6: 配置汇总** | `config-summary/` | `selectedPlanIds`, 方案列表 + 分布统计 | Mock (24 方案) |

### 5.3 步骤间联动（`modelConfig.ts` store）

```
Step 1 场景 → Step 2 主体（预填起止时间/水库/步长）
    ↓
Step 1 场景 → Step 4 算法（推荐模型/算法、联动目标）
    ↓
Step 2 组合 → Step 4 模型（筛选兼容模型）
    ↓
Step 4 目标 → Step 5 场景（关联约束参数）
```

联动数据定义在 `mock/model-config/linkage.ts`，目前均为**静态 Mock**，未接入真实 API。

### 5.4 算法参数（前端定义 vs 模型实际）

| 前端参数 ID | 前端默认值 | NSGA-II 模型实际 | 对应关系 |
|-------------|-----------|------------------|----------|
| `populationSize` | 200 | `pop` 入参 | ✅ 可直接对应 |
| `iterationCount` | 500 | `iterate` 入参 | ✅ 可直接对应 |
| `crossoverRate` | 0.9 | `genetic_operator.m` 已支持 Pc 参数传入 | ✅ 已实现参数化 |
| `mutationRate` | 0.1 | 无显式参数（由 `mu`, `mum` 控制） | ❌ 概念不匹配 |
| `eliteRate` | 0.05 | 无此参数（NSGA-II 用 `replace_chromosome`） | ❌ 不存在 |
| `crowdingFactor` | 2.0 | 无此参数 | ❌ 不存在 |

### 5.5 当前状态

- **API 集成**: 部分页面已接入真实 API，部分仍使用 Mock 数据：
  - ✅ 配置汇总页 → `POST /run` 提交任务
  - ✅ 过程透明页 → WebSocket 接收 progress + process_data 实时推送
  - ✅ 评价决策页 → `POST /evaluate` + `GET /evaluate/{job_id}`
  - ⬜ 模型配置 Step 1-5 展示 → 仍使用 Mock 数据
  - ⬜ 案例库、报表统计 → 仍使用 Mock 数据
- **运行端口**: 前端 dev server → `:3000`，后端 API → `:18080`
- **前后端对应关系**: 模型配置 Step 6（配置汇总）可组装 `RunRequest` 调用 `POST /run`，完成后跳转到过程透明页

---

## 六、前后端配置对齐

前端（Vue3）和后端（FastAPI）之间存在参数名、默认值和模型能力的差异。详细的对齐方案和分步实施计划见 [model-run-integration.md](model-run-integration.md)。

**主要差距：**
- 前端参数名（`populationSize`/`iterationCount`/`crossoverRate`）vs 后端模型参数（`pop`/`iterate`/`Pc`）
- 前端默认值（200/500）vs 后端默认值（15/20）
- 前端可调的 `mutationRate`/`eliteRate`/`crowdingFactor` 在模型中无对应参数
- 约束参数（起调水位、防凌流量）在模型中硬编码，但后端已支持动态注入
- 西线调水前端选项名与模型 `flag_xixian` 取值不完全一致

---

## 七、快速定位索引

### 7.1 摸清数据从哪来到哪去
```
data.xlsx 18 sheets → load_data.m (20 全局变量)
    → nsga_2_para.m / PAEM_para.m
    → evaluate_objective*.m (核心计算)
    → push_callback_data.m → http_callback_push.m → /cb → asyncio.Queue → WebSocket → 前端
    → write_json_log.m → *.jsonl 文件持久化
```

### 7.2 想修改模型参数
- 算法参数（pop, iterate, M, Q_sediment, K_mut）→ `nsga_2_para.m`/`PAEM_para.m` 函数签名
- 遗传算子参数（mu, mum）→ `genetic_operator.m` + 调用处的硬编码（Pc 已参数化，通过函数入参传入）
- 约束参数（起调水位、防凌流量、保证出力）→ `evaluate_objective*.m`
- 数据文件 / 西线调水 → `load_data.m`

### 7.3 想修改 Web 服务
- 配置 → `config.py`
- API 逻辑 → `main.py`
- MATLAB 调用 → `services/matlab.py`
- 任务队列 → `core/job_manager.py`
- WebSocket → `core/websocket.py` + `core/callback.py`
- 数据模型 → `schemas/job.py` / `schemas/result.py`

### 7.4 想修改前端
- 配置流程状态 → `stores/modelConfig.ts`
- 类型定义 → `types/model.ts`
- Mock 数据 → `mock/model-config/`
- 页面 UI → `views/model-config/`
- 组件 → `components/model-config/`
- 步骤间联动 → `mock/model-config/linkage.ts`

### 7.5 想匹配前后端配置（核心任务）
1. 前端 `types/model.ts` 定义配置结构
2. 前端 `stores/modelConfig.ts` 管理 6 步配置状态
3. 后端 `schemas/job.py` `RunRequest` 接收运行参数
4. 模型 `nsga_2_para.m` 函数签名接收 5 个参数（`pop, iterate, M, Q_sediment, Pc`）
5. 模型另有大量硬编码参数（mu, mum, Pc, 起调水位等）
6. 前后端配置参数名和默认值均不一致

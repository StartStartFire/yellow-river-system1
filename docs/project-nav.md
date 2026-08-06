# 项目目录导航

> 快速了解 `matlab-model/`（MATLAB 模型）、`backend-service/`（Python Web 服务）、`evaluation-model/`（评价系统）、`frontend-service/`（Vue3 前端）四个目录的结构与职责。
> 本文档为 AI 和开发者设计，帮助在不逐个读取文件的前提下迅速定位代码。

---

## 一、总览

```
F:\Model\yellow_river_project\
├── matlab-model/                     # MATLAB 多目标优化调度模型
│   ├── nsga_2_para.m          # NSGA-II 主循环（入口）
│   ├── PAEM_para.m            # PAEM 主循环（入口）
│   ├── evaluate_objective*.m  # 4 个评价函数（含 save_info 版本）
│   ├── *.m                    # 20 个辅助函数
│   ├── data.xlsx              # 输入数据（17 个 sheet）
│   ├── callback_config.txt    # 回调地址配置
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
│   ├── 使用说明.docx           # 本地文档
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
│       ├── mock/              # Mock 数据（暂未接入真实 API）
│       ├── views/             # 13 个页面视图
│       ├── components/        # 35+ 组件
│       └── layouts/           # 布局组件
│
├── docs/                      # 跨项目文档
│   ├── project-nav.md         # ← 本文档（项目目录导航）
│   ├── work-log.md            # AI 工作日志
│   ├── development-steps.md   # 分步实施计划（原始 6 步 ✅）
│   ├── technical-roadmap.md   # Web 服务化技术方案
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

### 2.1 文件清单与职责

| 文件 | 行数 | 职责 | 关键细节 |
|------|------|------|----------|
| `main.m` | ~15 | 程序入口 | 调用 `load_data` + `nsga_2_para` 或 `PAEM_para` |
| `nsga_2_para.m` | ~110 | **NSGA-II 主循环** | 接收 `(pop, iterate, M, Q_sediment)`；硬编码 `mu=20, mum=20`；每5代写JSONL+回调 |
| `PAEM_para.m` | ~130 | **PAEM 主循环** | 接收 `(pop, iterate, K_mut, M, Q_sediment)`；硬编码 `mu=20, mum=20`；最终做一次精确评价 |
| `load_data.m` | ~115 | **数据加载** | 读取 data.xlsx 的 17 个 sheet → 设置 ~20 个全局变量；`flag_xixian` 控制西线调水 |
| `evaluate_objective.m` | ~550 | **基础目标函数** | 四大约束：水量平衡、出力保证、生态流量、泥沙冲沙；起调水位 2580/1720 硬编码 |
| `evaluate_objective_NSGA2.m` | ~550 | NSGA-II 专用评估 | 同上，多加防凌流量处理逻辑（Qmin 硬编码） |
| `evaluate_objective_PAEM.m` | ~550 | PAEM 专用评估 | 同上，多加 PAEM 近似评价逻辑（K_mut 参数） |
| `initialize_population.m` | ~80 | 种群初始化 | 在 VarMin~VarMax 间均匀随机生成；汛期水位上升趋势修正 |
| `genetic_operator.m` | ~117 | **遗传操作** | SBX 交叉（Pc=0.9 硬编码）+ 多项式变异（Pm 隐式）；`mu`, `mum` 参数传入 |
| `non_domination_sort_mod.m` | - | 非支配排序 | 快速非支配排序 + 拥挤距离计算 |
| `tournament_selection.m` | ~115 | 锦标赛选择 | pool_size/2, tour=2；按 rank（小优先）→ crowding distance（大优先） |
| `replace_chromosome.m` | - | 种群替换 | 从合并种群中保留前 pop 个个体 |
| `mutation_one_variable.m` | ~13 | 单变量变异 | 多项式变异的一个变量版本 |
| `chz1.m` | - | 约束处理1 | 与出库流量相关的修正逻辑 |
| `chz2.m` | - | 约束处理2 | 与水库水位相关的修正逻辑 |
| `find_nondominated_solution.m` | - | 非支配解提取 | 从最终种群中提取 rank=1 的解 |
| `initialize_population.m` | - | 种群初始化 | 已在上方列出 |
| `write_json_log.m` | - | JSONL 日志写入 | 封装 `jsonencode` + `fflush` |
| `init_log_file.m` | - | 日志文件初始化 | 打开文件句柄 |
| `http_callback_push.m` | ~35 | **回调推送** | `persistent` 读取 callback_config.txt → `webwrite` POST → try-catch 静默降级，Timeout=1s |
| `preprocess_results_for_json.m` | ~25 | 结果预处理 | 递归处理 NaN/Inf → 字符串 |

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
http_callback_push.m → POST → Web 服务 /cb
     ↓
结果 → output.chromosome / chromosome_acc
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

- **`data.xlsx`** — 17 个 sheet，包含 54 年（1970-2023）实测数据
  - 水位-流量/库容曲线：`LONG-ZQ`, `LONG-ZV`, `LIU-ZQ`, `LIU-ZV`
  - 入流/区间：`LONGIN`, `LONG-LIU`, `LIU-LAN`
  - 用水/调水：`longliu_water`, `liulan_water`, `xixian_up`, `xixian_down`
  - 需水：`LAN`, `LAN-unagr`, `LAN-agr`
  - 生态/频率：`Q_eco`, `P`
  - 水位边界：`LONGLIU-BOUND`
  - 物理参数：`CANSHU`
- **`callback_config.txt`** — 一行 URL：`http://127.0.0.1:18080/cb`

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

| 方法 | 路径 | 请求/响应 | 说明 |
|------|------|-----------|------|
| GET | `/health` | `HealthResponse` | 健康检查 + Engine 状态 |
| POST | `/run` | `RunRequest` → `JobStatusResponse` | 提交优化任务，返回 job_id（含约束参数） |
| GET | `/status/{job_id}` | `JobStatusResponse` | 查询任务状态 |
| GET | `/jobs` | `list[JobSummary]` | 任务列表，可按 `?status=` 过滤 |
| GET | `/results/{job_id}` | `ResultResponse` | 获取 Pareto 解集 + evaluating 评价指标 |
| GET | `/process/{job_id}` | `{process_data}` | 补拉最新过程数据 🚧（MATLAB 侧未推送） |
| POST | `/evaluate` | `EvaluateRequest` → `EvaluateResponse` | 运行评价算法（NMF/PP/AHP_FUZZY/ALL） |
| GET | `/evaluate/{job_id}` | `EvaluateResponse` | 获取评价缓存结果 |
| POST | `/cb` | `CallbackPayload` → `CallbackResponse` | MATLAB 回调接收 |
| WS | `/ws/{job_id}` | — | WebSocket 实时订阅 |

### 3.3 通信链路

```
MATLAB (nsga_2_para.m)
  │ 每5代/每代 调用 http_callback_push.m
  │ webwrite POST → http://127.0.0.1:18080/cb
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
host: 127.0.0.1
port: 18080
cors_origins: ["http://localhost:3000", ...]
matlab_root: F:/Model/yellow_river_project/matlab-model
data_file: data.xlsx
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
| `evaluation_system/__init__.py` | **统一入口** | `run_complete_evaluation(data_matrix, config)` 一键运行 3 种算法 + 整合 |
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
  → run_complete_evaluation(matrix, config)
    → NMFAlgorithm.run()       → W, H, ranks, cost_history
    → PPAlgorithm.run()        → a, z, ranks, cost_history
    → FuzzyAlgorithm.run()     → final_scores, ranks, ahp_weights, 一级评价
    → RankSumTheory.integrate() → final_ranking (序号总和)
    → _build_evaluation_cache() → rankings + convergence + subsystem + raw_indicators
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
├── mock/                       # Mock 数据（所有页面，无真实 HTTP 调用）
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
| `crossoverRate` | 0.9 | `genetic_operator.m` 硬编码 0.9 | ⚠️ 模型目前硬编码 |
| `mutationRate` | 0.1 | 无显式参数（由 `mu`, `mum` 控制） | ❌ 概念不匹配 |
| `eliteRate` | 0.05 | 无此参数（NSGA-II 用 `replace_chromosome`） | ❌ 不存在 |
| `crowdingFactor` | 2.0 | 无此参数 | ❌ 不存在 |

### 5.5 当前状态

- **API 集成**: 前端目前**未接入**真实 API 调用（所有数据来自 Mock）
- **运行端口**: 前端 dev server → `:3000`，后端 API → `:18080`
- **前后端对应关系**: 6 步流程的配置数据理论上应组装为 `RunRequest` POST 到 `/run`，但该链路尚未实现

---

## 六、关键配置差距（前端 ↔ 后端 ↔ 模型）

### 6.1 算法参数（最突出的差距）

| 前端传参 | 模型实际接收 | 差距说明 |
|----------|-------------|----------|
| `populationSize` | `pop` | ✅ 一致，但默认值不同（前端 200 vs 后端 15） |
| `iterationCount` | `iterate` | ✅ 一致，但默认值不同（前端 500 vs 后端 20） |
| `crossoverRate` | 硬编码 `0.9` | ⚠️ 前端可调但模型不支持 |
| `mutationRate` | 无直接参数 | ❌ 前端可调但模型概念不同 |
| `eliteRate` | 无此参数 | ❌ |
| `crowdingFactor` | 无此参数 | ❌ |
| `mu` (SBX 指数) | 硬编码 `20` | ❌ 前端未暴露，模型硬编码 |
| `mum` (变异指数) | 硬编码 `20` | ❌ 前端未暴露，模型硬编码 |

### 6.2 场景约束参数

| 前端约束 | 模型对应 | 状态 |
|----------|----------|------|
| 西线调水 (`westRoute`) | `flag_xixian` (全无/全有/有上无下/有下无上) | ✅ 概念对应，但选项名不同 |
| 调沙流量 (`sedimentFlow`) | `Q_sediment` | ✅ 概念一致 |
| 生态流量 (`ecologicalFlow`) | `Q_eco`（从 Excel 读取） | ⚠️ 模型用 Excel 数据，前端是用户配置 |
| 防凌流量 (`icePreventionFlow`) | `Qmin` 硬编码 | ❌ 前端可配但模型硬编码 |

### 6.3 前端未覆盖的模型配置

- 起调水位（硬编码 2580/1720）
- 防凌流量硬编码 [610,420,420,420,420]
- 保证出力（龙羊峡 58.7 / 刘家峡 40 万kW）
- 装机容量（龙羊峡 128 / 刘家峡 122.5 万kW）
- 时段转换系数 `xishu`、天数 `t`
- Excel 数据文件选择

---

## 七、快速定位索引

### 7.1 摸清数据从哪来到哪去
```
data.xlsx 17 sheets → load_data.m (20 全局变量)
    → nsga_2_para.m / PAEM_para.m
    → evaluate_objective*.m (核心计算)
    → http_callback_push.m → /cb → asyncio.Queue → WebSocket → 前端
    → write_json_log.m → *.jsonl 文件持久化
```

### 7.2 想修改模型参数
- 算法参数（pop, iterate, M, Q_sediment, K_mut）→ `nsga_2_para.m`/`PAEM_para.m` 函数签名
- 遗传算子参数（mu, mum, Pc）→ `genetic_operator.m` + 调用处的硬编码
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
4. 模型 `nsga_2_para.m` 函数签名只接收 4 个参数
5. 模型另有大量硬编码参数（mu, mum, Pc, 起调水位等）
6. 前后端配置参数名和默认值均不一致

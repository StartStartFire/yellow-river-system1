# CLAUDE.md — 项目开发规范

## 项目概述

黄河上游**龙羊峡—刘家峡梯级水库多目标优化调度模型**的 MATLAB + Python Web 服务化项目。

**当前阶段：系统集成阶段** — 核心功能开发已全部完成（Web 服务模块化重构、评价系统集成、约束参数动态注入），当前重点为前后端联调（Mock 数据→真实 API）、过程透明化全链路实施、及剩余前端页面（案例库、报表统计等）的 API 对接。

- **MATLAB 模型**：`matlab-model/` — NSGA-II / PAEM 多目标优化调度模型
- **Python Web 服务**：`backend-service/` — FastAPI 封装，提供 HTTP API 和 WebSocket 实时推送

## 目录结构

```
F:\Model\NSGA2\
├── CLAUDE.md               # 本项目开发规范
│
├── matlab-model\            # MATLAB 模型目录（纯 MATLAB，不混入 Python 代码）
│   ├── nsga_2_para.m        # NSGA-II 主循环
│   ├── PAEM_para.m          # PAEM 主循环
│   ├── evaluate_objective.m  # 目标函数评估（基础版）
│   ├── evaluate_objective_NSGA2.m  # NSGA-II 专用评估
│   ├── evaluate_objective_PAEM.m   # PAEM 近似评估
│   ├── evaluate_objective_save_info.m  # 带详细过程结果返回的评价函数（新增）
│   ├── load_data.m          # 数据加载（Excel → 全局变量）
│   ├── initialize_population.m  # 种群初始化
│   ├── genetic_operator.m   # 遗传操作（SBX 交叉 + 多项式变异）
│   ├── tournament_selection.m   # 锦标赛选择
│   ├── non_domination_sort_mod.m  # 非支配排序
│   ├── replace_chromosome.m  # 种群替换
│   ├── chz1.m / chz2.m      # 一维线性插值
│   ├── mutation_one_variable.m   # 单变量变异（PAEM）
│   ├── find_nondominated_solution.m  # 非支配解提取（PAEM）
│   ├── find_representative_solution.m  # 代表性最优解选择（新增）
│   ├── write_json_log.m     # JSONL 日志写入
│   ├── init_log_file.m      # 日志文件初始化
│   ├── preprocess_results_for_json.m  # 结果预处理
│   ├── http_callback_push.m # HTTP 回调推送（新增 — 唯一侵入点）
│   ├── main.m               # 程序入口
│   ├── data.xlsx            # 输入数据（17 个 sheet）
│   ├── http_callback_push.m # HTTP 回调推送
│   ├── NSGA2_progress.jsonl # NSGA-II 进化日志
│   ├── *.jsonl / *.json     # PAEM 日志
│   └── .git\                # Git 仓库
│
├── backend-service\         # Python Web 服务目录（模块化架构）
│   ├── run.py               # 启动脚本
│   ├── requirements.txt     # 依赖清单
│   └── app/
│       ├── main.py          # FastAPI 入口（lifespan + 路由注册）
│       ├── config.py        # 全局配置（dataclass 单例）
│       ├── api/             # API 路由层（5 个路由器）
│       │   ├── health.py    # GET /health
│       │   ├── jobs.py      # POST /run, GET /status, /jobs, /results, /process
│       │   ├── evaluate.py  # POST /evaluate, GET /evaluate/{job_id}
│       │   ├── ws.py        # WS /ws/{job_id}
│       │   └── callback.py  # POST /cb
│       ├── core/            # 核心业务层（5 个模块）
│       │   ├── executor.py  # BaseExecutor 抽象 + TaskConfig/TaskResult
│       │   ├── job_manager.py  # JobManager 任务队列 + 状态机
│       │   ├── callback.py  # CallbackQueue（回调消息缓冲区）
│       │   └── websocket.py # ConnectionManager + broadcast_loop
│       ├── schemas/         # Pydantic 数据模型（5 个模型文件）
│       │   ├── job.py       # RunRequest, JobStatusResponse, JobSummary
│       │   ├── evaluate.py  # EvaluateRequest, EvaluateResponse
│       │   ├── result.py    # ResultResponse
│       │   └── callback.py  # CallbackPayload
│       └── services/        # 服务封装层
│           └── matlab.py    # MatlabExecutor（Engine 生命周期管理）
│
├── evaluation-model\        # 评价系统模块（Python 独立模块）
│   ├── evaluation_system/
│   │   ├── __init__.py      # run_complete_evaluation 入口
│   │   ├── algorithm_base.py    # 算法基类
│   │   ├── nmf_algorithm.py     # NMF 非负矩阵分解布谷鸟搜索
│   │   ├── pp_algorithm.py      # PP 投影寻踪布谷鸟搜索
│   │   ├── fuzzy_algorithm.py   # AHP 模糊综合评价
│   │   ├── rank_sum_theory.py   # 序号总和整合
│   │   ├── standardization_algorithm.py  # 标准化
│   │   ├── standardization_main.py
│   │   ├── unified_config.py    # 统一配置
│   │   └── unified_output.py    # 统一输出
│   ├── example_usage.py
│   └── 使用说明.docx
│
├── frontend-service\        # Vue3 + TypeScript 前端（独立项目）
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/index.ts      # 13 个路由
│       ├── stores/              # Pinia 状态管理
│       │   ├── app.ts
│       │   └── modelConfig.ts   # 6 步流程状态（核心）
│       ├── types/               # 7 个类型定义
│       │   ├── model.ts
│       │   ├── reservoir.ts
│       │   ├── common.ts
│       │   ├── process.ts
│       │   ├── evaluation.ts
│       │   ├── caseLibrary.ts
│       │   └── reportStatistics.ts
│       ├── mock/                # Mock 数据（暂未接入真实 API）
│       │   ├── model-config/    # 6 步流程 Mock
│       │   └── ...其他页面 Mock
│       ├── views/               # 13 个页面视图
│       │   ├── home/
│       │   ├── basic-data/
│       │   ├── water-condition/
│       │   ├── model-config/    # 6 步流程（核心功能）
│       │   │   ├── dispatch-scenario/
│       │   │   ├── dispatch-subject/
│       │   │   ├── model-data/
│       │   │   ├── model-algorithm/
│       │   │   ├── scenario-constraint/
│       │   │   └── config-summary/
│       │   ├── process-transparent/
│       │   ├── evaluation-decision/
│       │   ├── case-library/
│       │   └── report-statistics/
│       ├── components/          # 35+ 组件
│       └── layouts/MainLayout.vue
│
├── matlab-model\             # MATLAB 模型（含专属文档）
│   └── docs/                 # MATLAB 模型专属文档
│       ├── model-specification.md  # 模型技术规格书
│       ├── scheduling-rules.md     # 12 条调度规则
│       └── project-analysis.md     # 逆向分析报告
│
├── backend-service\          # Python Web 服务（含专属文档）
│   └── docs/                 # Web 服务专属文档
│       ├── api-reference.md  # API 参考文档
│       └── backend-architecture.md  # 后端架构梳理
│
├── evaluation-model\         # 评价系统（含专属文档）
│   └── docs/                 # 评价系统专属文档
│       └── evaluation-data-specification.md  # 评价模型数据产出规格
│
├── frontend-service\         # 前端项目（含专属文档）
│   └── docs/                 # 前端专属文档
│       └── 常见问题.md        # 前端开发常见问题
│
├── docs\                     # 跨项目文档（日志、导航、计划）
│   ├── work-log.md           # AI 工作日志
│   ├── project-nav.md        # 项目目录导航（跨项目总览）
│   ├── model-run-integration.md  # ⬜ 模型运行对接方案
│   ├── process-transparent-plan.md  # ⬜ 过程透明化方案
│   ├── data-flow.md          # ⬜ 全过程数据流向（目标设计）
│
├── README.md                # 项目说明（可选）
```

## 当前阶段策略

### 持续遵循的原则

- **目录分离**：MATLAB / Python 不交叉存放
- **模块职责单一**：一个文件只做一件事
- **配置收拢**：业务代码不出现硬编码路径
- **回调静默降级**：`try-catch` + `Timeout=1s`
- **Web 服务故障不影响 MATLAB 模型**

### 当前阶段重点

- **前后端联调**：逐步替换前端 Mock 数据为真实 API 调用
- **过程透明化**：实施 Phase E-G，打通 MATLAB 过程数据→前端实时图表
- **剩余页面对接**：案例库、报表统计等页面接入真实 API

## 开发流程规范

### 渐进式实现原则

1. **分步计划**：任何功能开发前，先分解为独立步骤，以清单形式列出，确认每一步的范围和前置条件
2. **分步实现**：一次只实现一步，完成并验证后再进入下一步，禁止一次性生成完整功能
3. **可验证中间态**：每一步完成后必须是可运行/可验证的状态（编译通过、可测试），不允许留下半成品
4. **变更最小化**：每一步只修改实现该步所必需的最少文件，不做超前设计或范围蔓延

### 模块化要求

5. **低耦合**：模块间通过明确的接口（函数签名、配置文件、消息队列）通信，不共享全局可变状态
6. **高内聚**：每个模块只负责一个职责，职责边界清晰，不跨域
7. **可复用**：通用逻辑抽取为独立函数/类，避免代码重复
8. **可持续维护**：代码注释说明"为什么"而非"是什么"，复杂逻辑必须有文档或伪代码说明

### 复杂任务处理

9. **Sub-agent 拆分**：当一个任务涉及多个领域（如同时修改 MATLAB 和 Python 代码）、或多个文件、或需先调研再决策时，应将调研/分析工作委托给 sub-agent（使用 Agent 工具），本 agent 聚焦于决策和实现
10. **先读后写**：对不熟悉的代码段，先委托 sub-agent 阅读分析并给出摘要，再决定修改方案
11. **变更记录**：每次 sub-agent 完成工作后，将关键结论（文件路径、函数名、依赖关系）记录到 memory，便于后续步骤查阅

### 沟通规范

12. **方案先行**：对不确定的实现方案，先询问用户确认，再动手编码
13. **透明进度**：多步任务执行时，每步完成后同步进度和下一步计划

### 通用原则

14. **Web 服务目录与模型目录严格分离**：MATLAB 文件归 `matlab-model/`，Python 文件归 `backend-service/`，不交叉存放
15. **不改 MATLAB 模型核心逻辑**：新增 `http_callback_push.m` 作为唯一的"侵入点"，不修改 `evaluate_objective_*`、`load_data` 等核心计算文件（除非修 Bug）
16. **静默降级原则**：Web 服务的任何故障不影响 MATLAB 模型的正常运行。回调推送失败时应当 try-catch 静默降级，数据仍通过原有的 JSONL 文件机制持久化
17. **临时测试规范**：AI 和开发者的快速验证脚本一律放在根目录 `_sandbox/` 下（已在 `.gitignore` 中），用完及时删除；禁止在 `_sandbox/` 之外的目录创建临时测试文件

### MATLAB 代码规范

1. **文件名用小写 + 下划线**：如 `nsga_2_para.m`、`non_domination_sort_mod.m`
2. **全局变量**：`global` 声明统一写在函数头部，使用全大写命名：`LONG_ZQ`、`VarMax`、`Y` 等
3. **注释语言**：中文注释（项目既有风格）
4. **新增函数**：必须包含完整的 H1 帮助文本（函数说明行 + 参数说明）
5. **try-catch 的使用**：推送类操作（如 `webwrite`）必须用 try-catch 包裹，防止异常向上传播
6. **JSONL 文件写入**：使用 `write_json_log` 函数（已封装好 `jsonencode` + `fflush`），不要直接操作文件 I/O
7. **`persistent` 变量的使用**：适合缓存配置、URL 等只需加载一次的数据

### Python 代码规范

1. **命名风格**：模块/变量/函数用 `snake_case`，类用 `PascalCase`
2. **类型注解**：函数参数和返回值标注类型，内部变量从简（系统集成阶段可接受，上线前补齐）
3. **虚拟环境**：使用 venv 或 conda 创建隔离环境，Python 版本固定为 3.11，虚拟环境目录不提交到 git
4. **异步优先**：I/O 操作（文件、网络）使用 `async/await`；CPU 密集型任务（MATLAB 调用）使用 `run_in_executor`
5. **配置收拢**：端口、路径、超时等参数写在 `config.py` 的 `Config` dataclass 中，不硬编码在业务代码里
6. **Pydantic 验证**：API 请求/响应和回调数据使用 Pydantic 模型校验
7. **错误处理**：API 端点返回结构化的错误响应（`{"detail": "..."}`），不抛裸异常

### MATLAB ↔ Python 通信规范

1. **唯一通信方式**：MATLAB 调用 `http_callback_push.m` → `webwrite` → HTTP POST → FastAPI `/cb` 端点
2. **不使用 `py.` 桥接**：MATLAB 嵌入式 Python 与宿主 Python 位于不同进程，无法共享内存对象
3. **数据格式**：MATLAB 的 `struct` 通过 `webwrite` 发送时自动转为 JSON，Python 侧按收到的 JSON 解析
4. **回调推送**：`http_callback_push.m` 写死回调地址 `127.0.0.1:18080/cb`，无需外部配置
5. **回调端口**：固定 `127.0.0.1:18080`，仅本地监听，不对外开放

## 常见注意事项

| 事项                       | 说明                                                         |
| -------------------------- | ------------------------------------------------------------ |
| **MATLAB Engine 线程安全** | 非线程安全，必须串行调用。使用 `ThreadPoolExecutor(max_workers=1)` |
| **Python 版本兼容**        | MATLAB R2024a 的 Engine API 仅支持 Python 3.9~3.11，固定使用 3.11 |
| **虚拟环境**              | Web 服务须在 venv 或 conda 隔离环境中运行，不直接使用全局 Python |
| **`webwrite` 超时**        | 设置为 1 秒，避免回调阻塞优化主循环                          |
| **`numel` Bug**            | `numel(A, condition)` 不符合标准 MATLAB 语法，第二个参数被忽略，应改用 `sum(A==0)` |
| **工作目录**               | MATLAB Engine 启动后必须 `eng.cd()` 到 `matlab-model/` 目录，否则 `xlsread` 找不到文件 |
| **入口脚本**               | 程序入口为 `main.m`，Web 服务通过 `eng.nsga_2_para` 直接调用主循环，不经过 `main.m` |
| **数据加载**               | 使用 `load_data.m` 加载 Excel 数据                           |
| **内存管理**               | 多次优化后 MATLAB 进程内存可能增长，建议定期重启引擎         |

## 技术文档索引

> 文档按"谁所属"分散在各子项目 `docs/` 目录下，跨项目文档留在根 `docs/`。

### 子项目专属文档

| 归属 | 文档 | 路径 |
|------|------|------|
| **matlab-model/** (MATLAB) | 模型技术规格书 | [matlab-model/docs/model-specification.md](matlab-model/docs/model-specification.md) |
| | 调度规则（12 条） | [matlab-model/docs/scheduling-rules.md](matlab-model/docs/scheduling-rules.md) |
| | 项目逆向分析报告 | [matlab-model/docs/project-analysis.md](matlab-model/docs/project-analysis.md) |
| **backend-service/** (Python) | API 参考文档 | [backend-service/docs/api-reference.md](backend-service/docs/api-reference.md) |
| | 后端架构梳理 | [backend-service/docs/backend-architecture.md](backend-service/docs/backend-architecture.md) |
| **evaluation-model/** (Python) | 评价模型数据产出规格 | [evaluation-model/docs/evaluation-data-specification.md](evaluation-model/docs/evaluation-data-specification.md) |
| **frontend-service/** (Vue3) | 前端开发常见问题 | [frontend-service/docs/常见问题.md](frontend-service/docs/常见问题.md) |

### 跨项目文档（根 docs/）

| 文档 | 说明 |
|------|------|
| [项目目录导航](docs/project-nav.md) | 四端（MATLAB/Web/评价/前端）目录结构与职责总览 |
| [AI 工作日志](docs/work-log.md) | 完成任务记录 |
| [模型运行对接方案](docs/model-run-integration.md) | ⬜ Phase A-D 前后联调（待实施） |
| [过程透明化方案](docs/process-transparent-plan.md) | ⬜ Phase E-G 过程透明化（待实施） |
| [全过程数据流向](docs/data-flow.md) | ⬜ 目标状态设计（待实施） |

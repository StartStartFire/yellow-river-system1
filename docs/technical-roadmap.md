# 梯级水库多目标优化模型 Web 服务化技术方案

> 版本：v1.0 → v1.1  
> 日期：2026-07-11（初版）→ 2026-08-04（更新）  
> 状态：**原型阶段（Step 1-6）已完成**，进入功能扩展期
> 
> 具体执行步骤见 [development-steps.md](development-steps.md)，每步可独立验证。
> 完成后更新 [work-log.md](work-log.md)。

---

## 1. 目标

将现有的 **龙羊峡—刘家峡梯级水库多目标优化调度模型**（MATLAB R2024a）封装为 **FastAPI Web 服务**，实现：

- 通过 HTTP API 提交 NSGA-II / PAEM 优化任务
- 优化过程中实时推送每代进化进度到前端（WebSocket）
- 优化完成后获取最终 Pareto 解集
- Web 服务目录与模型目录完全分离，各自独立维护

---

## 2. 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│  机器 A（开发机，127.0.0.1）                                              │
│                                                                         │
│  ┌────────────────────────────────────┐  ┌────────────────────────────┐ │
│  │  F:\Model\yellow_river_project\web-service\             │  │  F:\Model\yellow_river_project\matlab-model\   │ │
│  │  (Python FastAPI Web Server)       │  │  (MATLAB 模型目录)          │ │
│  │                                    │  │                            │ │
│  │  ┌──────────┐  ┌────────────────┐  │  │  ┌──────────────────────┐ │ │
│  │  │ HTTP API  │  │ WebSocket Hub  │  │  │  │ MATLAB Engine 进程   │ │ │
│  │  │ GET/POST  │  │ WS /ws/{id}   │  │  │  │  (常驻内存)           │ │ │
│  │  └─────┬────┘  └───────┬────────┘  │  │  │                      │ │ │
│  │        │               │           │  │  │  nsga_2_para.m       │ │ │
│  │  ┌─────▼───────────────▼────────┐  │  │  │    ↓ 每代末尾         │ │ │
│  │  │    job_manager               │  │  │  │  http_callback_push  │ │ │
│  │  │     └─ executor (抽象接口)    │  │  │  │  → webwrite POST     │ │ │
│  │  │           └─ MatlabExecutor  │◀─┼──┼──│    → /cb             │ │ │
│  │  │              (串行调用)       │  │  │  │                      │ │ │
│  │  └──────────────────────────────┘  │  │  │  JSONL 文件写入      │ │ │
│  │                                    │  │  │  (持久化 fallback)   │ │ │
│  │  ┌──────────────────────────────┐  │  │  │                      │ │ │
│  │  │     asyncio.Queue            │  │  │  └──────────────────────┘ │ │
│  │  │     (消息缓冲区)             │◀─┼──┼──│  http_callback_push  │ │ │
│  │  └──────────────────────────────┘  │  │                           │ │
│  └────────────────────────────────────┘  └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                              浏览器 / 客户端
```

### 2.1 分层职责

| 层 | 技术栈 | 职责 |
|---|---|---|
| **Web 服务层** | FastAPI + uvicorn | API、WebSocket、任务管理、回调接收 |
| **引擎管理层** | `matlab.engine` | 启动/管理 MATLAB 进程，串行执行优化任务 |
| **实时数据层** | `webwrite` → HTTP POST → `asyncio.Queue` | MATLAB 每代结束后推送进度数据 |
| **持久化层** | `write_json_log` → JSONL 文件 | 数据持久化存储，与原有机制完全兼容 |
| **模型计算层** | MATLAB R2024a | NSGA-II / PAEM 优化计算 |

---

## 3. 目录结构

```
F:\Model\yellow_river_project\
├── matlab-model\                           ← 模型目录（纯 MATLAB，已有）
│   ├── nsga_2_para.m                ← NSGA-II 主循环
│   ├── PAEM_para.m                  ← PAEM 主循环
│   ├── evaluate_objective.m          ← 目标函数评估（基础版）
│   ├── evaluate_objective_NSGA2.m    ← NSGA-II 专用评估
│   ├── evaluate_objective_PAEM.m     ← PAEM 专用评估
│   ├── load_data.m                   ← 数据加载
│   ├── initialize_population.m       ← 种群初始化
│   ├── genetic_operator.m            ← 遗传操作
│   ├── tournament_selection.m        ← 锦标赛选择
│   ├── non_domination_sort_mod.m     ← 非支配排序
│   ├── replace_chromosome.m          ← 种群替换
│   ├── chz1.m / chz2.m              ← 插值函数
│   ├── mutation_one_variable.m       ← 变量变异（PAEM）
│   ├── find_nondominated_solution.m  ← 非支配解筛选（PAEM）
│   ├── write_json_log.m              ← JSONL 日志写入
│   ├── init_log_file.m               ← 日志文件管理
│   ├── preprocess_results_for_json.m ← JSON 预处理
│   ├── data.xlsx                     ← 输入数据
│   ├── main.m                        ← 入口脚本
│   ├── NSGA2_progress.jsonl          ← 已有（持久化日志）
│   └── docs\
│       ├── model-specification.md    ← 已有：模型技术规格
│       ├── project-analysis.md       ← 已有：项目分析
│       └── scheduling-rules.md       ← 已有：调度规则
│
├── backend-service\                      ← Web 服务目录（模块化架构）
│   ├── run.py                        ← 启动脚本
│   ├── requirements.txt              ← 依赖清单
│   ├── app/
│   │   ├── main.py                   ← FastAPI 入口 + 生命周期 + 路由注册
│   │   ├── config.py                 ← 全局配置（端口、路径、默认参数）
│   │   ├── api/                      ← 路由层（5 个路由器）
│   │   ├── core/                     ← 业务核心（4 个模块）
│   │   ├── schemas/                  ← Pydantic 模型（4 个文件）
│   │   └── services/                 ← MATLAB Engine 封装
│   └── docs/                         ← 专属文档
│       ├── api-reference.md
│       └── backend-architecture.md
│
├── evaluation-model\                  ← 评价系统
│   ├── evaluation_system/
│   └── docs/
│
└── README.md

### 3.1 分离原则

| 关注点 | 归属目录 | 说明 |
|---|---|---|
| MATLAB 模型代码 | `nsga2\` | 所有 `.m` 文件、`data.xlsx` |
| 模型运行的日志输出 | `nsga2\` | JSONL 文件和 `json_logs*` 目录 |
| Python Web 代码 | `web-service\` | 所有 `.py` 文件 |
| Python 依赖管理 | `web-service\` | `requirements.txt`、虚拟环境 |
| **共享配置** | `nsga2\callback_config.txt` | MATLAB 读取的推送地址 |

工作流：`services/matlab.py`（MatlabExecutor）启动引擎后 `cd` 到 `matlab-model/`，所有文件操作都在模型目录内完成，Web 服务目录保持干净。

---

## 4. 技术选型

| 组件 | 选择 | 理由 |
|---|---|---|
| Web 框架 | **FastAPI** | 原生 async/await、WebSocket 支持、自动 OpenAPI 文档 |
| 异步服务器 | **uvicorn** | FastAPI 标准搭配 |
| Python 版本 | **3.11** | MATLAB R2024a Engine API 兼容范围 3.9~3.11 |
| 虚拟环境 | **venv 或 conda** | 隔离项目依赖，不污染全局 Python |
| MATLAB 集成 | **matlab.engine** (官方 API) | 零代码改造、MATLAB R2024a 完整版已安装 |
| 实时数据通道 | **webwrite → HTTP POST** | 避免"两个 Python 解释器"问题，纯 MATLAB 实现 |
| 数据持久化 | **JSONL 文件**（已有） | 模型原有机制，与 Web 服务无关，作为 fallback |
| 任务队列 | **asyncio.Queue + 单线程执行器** | 开发环境足够，无需外部依赖 |
| 回调端口 | **127.0.0.1:18080** | 仅本地监听，MATLAB 通过 localhost 访问 |

### 4.1 为什么用 `webwrite` 而不是 `py.` 桥接

MATLAB 的 `py.` 调用的是 MATLAB 进程**内部自带的嵌入式 Python 解释器**，与宿主 Python（运行 FastAPI 的那个）位于不同进程，无法直接共享 `asyncio.Queue`。

`webwrite` 是 MATLAB 内置函数，通过 HTTP POST 将数据发送到 FastAPI 的 `/cb` 端点，**两个进程通过 TCP/IP 通信，完全解耦**。

```
MATLAB 进程                          Python 进程
┌─────────────────┐                 ┌──────────────────┐
│  webwrite(url,   │── HTTP POST ──▶│  /cb 端点         │
│    payload)      │                 │    ↓              │
│   try-catch 包裹  │                 │  asyncio.Queue   │
│   Timeout=1s     │                 │    ↓              │
│   静默降级        │                 │  WebSocket 广播   │
└─────────────────┘                 └──────────────────┘
```

---

## 5. 实现步骤分解

> ✅ = 已完成　⏳ = 进行中　⬜ = 待实施

采用渐进式实现，每一步可独立验证，前一步完成后才能进入下一步。

```
✅ Step 1: Web 服务骨架
   ├─ 创建 backend-service/ 目录结构及空模块桩
   ├─ 定义核心 Pydantic 模型（含回调数据校验）
   └─ 验证: GET /health 返回 {"status": "ok"}
         ↓
✅ Step 2: 任务生命周期管理（无 MATLAB）
   ├─ 实现 executor 抽象接口
   ├─ 实现 BaseExecutor + MockExecutor（模拟 MATLAB 调用，原型临时用）
   ├─ 实现 job_manager（队列 + 状态机）
   └─ 验证: POST /run → status 可从 queued→running→completed 迁移
         ↓
✅ Step 3: MATLAB Engine 集成
   ├─ 实现 MatlabExecutor（继承 executor 接口）
   ├─ 可配置路径（config.py），去除硬编码
   └─ 验证: 后台线程成功调用 eng.nsga_2_para 并返回结果
         ↓
✅ Step 4: WebSocket + /cb 端点（接收侧就绪）
   ├─ 实现 callback.py（/cb 端点 + Pydantic 校验）
   ├─ 实现 websocket.py（从 Queue 消费并广播）
   └─ 验证: curl POST /cb → WebSocket 客户端收到广播
         ↓
✅ Step 5: MATLAB 回调推送（发送侧接入）
   ├─ 新增 http_callback_push.m + callback_config.txt
   ├─ 修改 nsga_2_para.m / PAEM_para.m 各 +1 行
   └─ 验证: MATLAB 运行时向 /cb 发送 POST，Python 收到并存入 Queue
         ↓
✅ Step 6: 结果查询 + 联调
   ├─ 实现 GET /results/{id}（从 JSONL 文件读取）
   └─ 验证: 全链路 POST→WS→GET 端到端通过
```

### 超出原计划的额外完成工作

```
✅ Web 服务模块化重构（扁平 7 文件 → api/core/schemas/services 四层架构）
✅ 评价系统集成（NMF/PP/AHP_FUZZY 三种算法 + RankSumTheory 整合）
✅ POST /evaluate + GET /evaluate/{job_id} 端点
✅ GET /process/{job_id} 过程数据补拉端点
✅ RunRequest 扩展（crossover_rate, flag_xixian, year_start/end, 起调水位, 防凌流量）
✅ evaluate_objective_save_info.m 新增（带详细过程结果返回）
✅ 约束参数动态注入（起调水位、防凌流量、年份范围通过 eng.eval() 传入）
✅ Vue3 前端项目搭建（13 视图、35+ 组件）
```

### 待实施工作（详见独立计划文档）

```
⬜ Phase A: 纯前端改造（类型/Mock/Store/视图对齐模型） — model-run-integration.md
⬜ Phase B: MATLAB 遗传算子参数化（Pc 硬编码→可传入） — model-run-integration.md
⬜ Phase C: 后端 Pc 参数传递 + 前端联调 — model-run-integration.md
⬜ Phase D: 前后端端到端联调 — model-run-integration.md
⬜ Phase E: MATLAB 过程透明化改造（evaluate nargout>1 + 增强回调） — process-transparent-plan.md
⬜ Phase F: 后端过程透明化改造（/cb 区分两种 type + 存储） — process-transparent-plan.md
⬜ Phase G: 前端过程透明化改造（页面对接真实 WS） — process-transparent-plan.md
```

### 5.1 Step 5 详细设计：MATLAB 回调推送

#### 新增文件：`http_callback_push.m`

**位置**：`matlab-model/http_callback_push.m`

**功能**：HTTP 回调推送的统一入口，被主循环文件调用。

```matlab
function http_callback_push(data_type, data)
% http_callback_push - 通过 webwrite 实时推送数据到 Web 服务
% 输入参数:
%   data_type - 'progress'
%   data      - MATLAB 结构体
%
% 通信方式：读取 callback_config.txt 获取推送 URL，
%           通过 webwrite POST JSON 到 Web 服务回调端点。
% 失败行为：try-catch 静默降级，不影响模型运行。

    persistent callback_url
    if isempty(callback_url)
        fid = fopen('callback_config.txt', 'r');
        if fid ~= -1
            callback_url = strtrim(fgets(fid));
            fclose(fid);
        else
            callback_url = 'http://127.0.0.1:18080/cb';
        end
    end

    try
        payload = struct();
        payload.type = data_type;
        payload.data = data;

        options = weboptions('MediaType', 'application/json', ...
                             'Timeout', 1, ...
                             'ContentType', 'text');
        webwrite(callback_url, payload, options);
    catch
        % 静默降级：Web 服务未就绪不影响模型
    end
end
```

#### 新增文件：`callback_config.txt`

**位置**：`matlab-model/callback_config.txt`

**内容**（单行文本）：
```
http://127.0.0.1:18080/cb
```

#### 修改：`nsga_2_para.m`

**修改位置**：第 84~92 行，日志记录段落末尾，`write_json_log` 之后插入一行：

```matlab
    http_callback_push('progress', json_data);  % 第 5 步新增
```

#### 修改：`PAEM_para.m`

**修改位置**：第 92~101 行，日志记录段落末尾，`write_json_log` 之后插入一行：

```matlab
    http_callback_push('progress', json_data);  % 第 5 步新增
```

#### 不改动的文件（全生命周期均不改动）

| 文件 | 不改的原因 |
|---|---|
| `evaluate_objective.m` | 纯计算函数，不参与日志或推送链路 |
| `evaluate_objective_NSGA2.m` | 同上 |
| `evaluate_objective_PAEM.m` | 同上 |
| `load_data.m` | 数据加载逻辑不变 |
| `initialize_population.m` | 初始化的评估仍走 `evaluate_objective.m` |
| `write_json_log.m` | 文件写入逻辑不变，不是推送链路的一部分 |
| `main.m` | 入口脚本，仅用于命令行调用 |

---

## 6. Python Web 服务概要设计

### 6.1 模块职责

| 模块 | 文件 | 核心职责 |
|---|---|---|
| 入口 | `main.py` | uvicorn 启动、FastAPI app 实例化、生命周期钩子 |
| 配置 | `config.py` | 全局配置单例：服务器端口、MATLAB 路径、回调地址、默认任务参数 |
| 数据模型 | `schemas/job.py` / `schemas/evaluate.py` | Pydantic 模型：请求/响应/WebSocket 消息/**回调数据校验** |
| 执行器抽象 | `core/executor.py` | 任务执行器接口定义（抽象基类），独立于具体实现，可 mock 测试 |
| 引擎管理 | `services/matlab.py` | MatlabExecutor：启动/关闭/重启引擎，串行执行优化任务 |
| 任务管理 | `job_manager.py` | 任务队列、状态管理，通过 `executor` 接口执行任务（不直接依赖 MATLAB） |
| 回调接收 | `callback.py` | `POST /cb` 路由，Pydantic 校验后写入 `asyncio.Queue` |
| WebSocket | `websocket.py` | 连接管理、从 Queue 消费并广播 |

#### 配置模型

使用 `dataclass` 将所有可变参数收拢到一处，原型阶段无需外部依赖或环境变量加载：

```python
# config.py
from dataclasses import dataclass

@dataclass
class Config:
    # 服务器
    host: str = "127.0.0.1"
    port: int = 18080

    # CORS（允许的前端 origin 列表）
    cors_origins: list[str] = None  # 默认 localhost:3000/3001

    # MATLAB 路径
    @property
    def matlab_root(self) -> str:
        return str(_PROJECT_ROOT / "matlab-model")

    data_file: str = "data.xlsx"

    # 回调
    callback_host: str = "127.0.0.1"
    callback_port: int = 18080
    callback_timeout: float = 1.0

    @property
    def callback_url(self) -> str:
        return f"http://{self.callback_host}:{self.callback_port}/cb"

    # 默认任务参数
    default_pop: int = 15
    default_iterate: int = 20
    default_m: int = 2
    default_q_sediment: float = 1800.0
    default_k_mut: int = 50


config = Config()  # 全局单例
```

关键设计：
- **全在 `Config` 类中**，找配置只需打开一个文件，不散落在各模块里
- **所有路径去掉硬编码**：`matlab_root`、`callback_host:port` 等均统一在此修改
- **换机器只需改 `matlab_root`** 一行即可运行

### 6.2 API 端点设计

| 方法 | 路径 | 功能 | 说明 |
|---|---|---|---|
| `GET` | `/health` | **健康检查** | 返回服务状态、引擎是否就绪 |
| `POST` | `/run` | 提交优化任务 | 返回 `job_id`，异步执行 |
| `GET` | `/status/{job_id}` | 查询任务状态 | 返回当前状态、进度、开始时间 |
| `GET` | `/results/{job_id}` | 获取最终结果 | 从 JSONL 文件读取最终代 Pareto 解集，不依赖 MATLAB 返回值 |
| `GET` | `/jobs` | 列出所有任务 | 支持过滤（running/completed/failed） |
| `WS` | `/ws/{job_id}` | WebSocket 实时订阅 | 接收该任务的 progress/log 消息 |
| `POST` | `/cb` | **MATLAB 回调入口** | 仅 `127.0.0.1` 可访问，Pydantic 校验后入队 |

#### 健康检查

```python
# main.py
@app.get("/health")
async def health():
    engine_ready = executor is not None and executor.is_alive()
    return {
        "status": "ok" if engine_ready else "degraded",
        "engine": "ready" if engine_ready else "not started",
        "version": "1.0.0"
    }
```

### 6.3 WebSocket 消息协议

所有 WebSocket 消息使用统一信封格式：

```json
{
  "type": "progress | log | status",
  "job_id": "uuid-string",
  "timestamp": "2026-07-11 14:30:00",
  "payload": { ... }
}
```

#### 消息类型 `progress`

```json
{
  "type": "progress",
  "job_id": "a1b2c3d4",
  "timestamp": "2026-07-11 14:30:00",
  "payload": {
    "iteration": 5,
    "total_iterations": 20,
    "progress_percent": 25.0,
    "objective_values": [[12.3, 45.6], [14.1, 43.2]],
    "algorithm": "nsga2"
  }
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `iteration` | int | 当前代数（1-based） |
| `total_iterations` | int | 总代数 |
| `progress_percent` | float | 进度百分比 |
| `objective_values` | `N×M` array | 当前种群所有个体的目标函数值 |
| `algorithm` | string | `"nsga2"` 或 `"paem"` |

#### 消息类型 `status`

```json
{
  "type": "status",
  "job_id": "a1b2c3d4",
  "timestamp": "2026-07-11 14:29:50",
  "payload": {
    "status": "running | completed | failed",
    "message": "NSGA-II 优化开始"
  }
}
```

#### 消息类型 `log`

```json
{
  "type": "log",
  "job_id": "a1b2c3d4",
  "timestamp": "2026-07-11 14:29:55",
  "payload": {
    "level": "info | warn | error",
    "message": "种群初始化完成，pop=15"
  }
}
```

### 6.4 回调数据格式与校验（Pydantic 模型）

MATLAB 通过 `webwrite` 发送到 `/cb` 端点的数据，由 Pydantic 模型在 Python 侧做结构化校验：

```python
# models.py

class CallbackPayload(BaseModel):
    """MATLAB 回调推送的顶层结构校验"""
    type: str                    # 'progress'
    data: dict                   # 具体的进度数据

class CallbackResponse(BaseModel):
    """/cb 端点返回确认"""
    received: bool
    job_id: str | None = None
```

`callback.py` 接收时先做 Pydantic 校验，再入队列：

```python
@app.post("/cb")
async def callback(payload: CallbackPayload):
    # Pydantic 自动校验字段类型，非法数据直接返回 422
    await queue.put(payload)
    return CallbackResponse(received=True)
```

### 6.5 任务生命周期

```
QUEUED → RUNNING → COMPLETED
                    → FAILED
```

| 状态 | 说明 |
|---|---|
| `queued` | 任务已创建，等待后台线程执行 |
| `running` | MATLAB 引擎正在执行优化 |
| `completed` | 优化完成，结果可获取 |
| `failed` | 优化过程出错 |

### 6.6 Executor 抽象接口

`executor.py` 定义任务执行器的抽象接口，使 `job_manager` 不直接依赖 MATLAB，可替换为不同的执行器实现：

```python
# executor.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class TaskConfig:
    algorithm: str    # 'nsga2' | 'paem'
    pop: int
    iterate: int
    M: int
    Q_sediment: float
    K_mut: int | None = None  # PAEM 专用

class TaskResult:
    """优化任务执行结果"""
    chromosome: list  # Pareto 解集矩阵
    # 实际数据通过 JSONL 文件持久化，result 仅含摘要

class BaseExecutor(ABC):
    @abstractmethod
    async def start(self):
        """初始化执行器（启动引擎、加载数据）"""
        ...

    @abstractmethod
    async def run(self, task: TaskConfig) -> TaskResult:
        """执行一次优化任务"""
        ...

    @abstractmethod
    async def stop(self):
        """关闭执行器，释放资源"""
        ...

class MatlabExecutor(BaseExecutor):
    """Step 3 实现：真正的 MATLAB Engine 调用"""
    ...
```

### 6.7 Engine 生命周期管理

```
FastAPI 启动
  │
  ├─ executor = MatlabExecutor(config)    ← 通过 executor 抽象接口
  │     ├─ eng = matlab.engine.start_matlab()
  │     ├─ eng.cd(config.matlab_root)     ← 从 config 读取
  │     └─ eng.load_data(config.data_file, config.flag_xixian)
  │
  ├─ job_manager = JobManager(executor)   ← job_manager 不直接依赖 MATLAB
  │
  ├─ 后台线程（单线程执行器）启动
  │
  ├─ 等待任务...
  │     └─ await executor.run(...)        ← 每次任务通过 executor 接口执行
  │
  └─ FastAPI 关闭
        └─ executor.stop()
              └─ eng.quit()
```

**线程安全**：MATLAB Engine 不是线程安全的。后台使用 `ThreadPoolExecutor(max_workers=1)` 串行执行所有任务，配合 `asyncio.get_event_loop().run_in_executor()` 实现异步调用。

---

## 7. 数据流全链路

```
用户 → POST /run { algorithm, pop, iterate, M, Q_sediment }
  │
  ├─ 返回 { job_id: "abc-123", status: "queued" }
  │
  ├─ job_manager 通过 executor 启动任务
  │     └─ executor.run(...)
  │           ├─ 路径: config.matlab_root (可配置)
  │           └─ MATLAB: nsga_2_para(pop, iterate, M, Q_sediment)
  │                 │
  │                 ├─ initialize_population()
  │                 │     └─ evaluate_objective() → JSONL 写文件
  │                 │
  │                 ├─ [迭代循环 i=1→20]
  │                 │     │
  │                 │     ├─ tournament_selection()
  │                 │     ├─ genetic_operator()
  │                 │     ├─ evaluate_objective_NSGA2() → JSONL 写文件
  │                 │     ├─ non_domination_sort_mod()
  │                 │     ├─ replace_chromosome()
  │                 │     │
  │                 │     └─ 记录日志:
  │                 │           ├─ write_json_log() → NSGA2_progress.jsonl
  │                 │           └─ http_callback_push('progress', data)
  │                 │                 │
  │                 │                 ▼
  │                 │           webwrite('http://127.0.0.1:18080/cb', payload)
  │                 │                 │
  │                 │                 ▼  (HTTP POST, 同一台机器)
  │                 │           FastAPI /cb 端点
  │                 │                 │
  │                 │                 ▼
  │                 │           asyncio.Queue.put_nowait(msg)
  │                 │                 │
  │                 │                 ▼
  │                 │           broadcast_loop()
  │                 │                 │
  │                 │                 ▼
  │                 │           所有 WS /ws/{job_id} 客户端
  │                 │
  │                 └─ [循环结束] 返回结果
  │
  └─ 后台线程: 结果写入 job_manager._results[job_id]
```

---

## 8. 错误处理策略

| 故障场景 | 影响 | 处理方式 |
|---|---|---|
| **Web 服务未启动** | MATLAB 的 `webwrite` 超时 | `try-catch` 静默降级，数据仍在 JSONL 文件中 |
| **MATLAB webwrite 超时** | 推送延迟，模型不中断 | `Timeout=1` 秒，不影响优化主循环 |
| **MATLAB 引擎崩溃** | 当前任务失败 | `job_manager` 捕获异常，状态设为 `failed`；FastAPI 自动重启引擎 |
| **WebSocket 断开** | 前端收不到后续推送 | 后台继续运行，任务状态和结果不受影响 |
| **多个任务排队** | 后续任务等待 | 单线程执行器天然串行，返回排队状态给客户端 |
| **前端重复连接** | 收到重复消息 | WebSocket 按 `job_id` 分组，不做去重（消息量小，可接受） |

---

## 9. 已知限制与注意事项

1. **MATLAB Engine 不是线程安全的**：必须串行执行任务，高并发场景需引入引擎池
2. **`matlab.engine` 仅支持 Python 3.9~3.11**：当前 Python 3.11 符合要求
3. **`xlsread` 不依赖 Excel**：纯数值文件，MATLAB 自有实现可解析
4. **程序入口兼容 Engine 模式**：`main.m` 含 `clc`，仅用于命令行交互；Engine 模式通过 `eng.nsga_2_para` 直接调用主循环，不经过 `main.m`
5. **回调端口只监听 127.0.0.1**：不对外暴露，安全性由本地回环地址保证
6. **长时间运行的任务**：建议前端显示进度提示，防止用户误以为服务无响应
7. **MATLAB 进程内存**：多次优化后建议定期重启引擎，避免内存持续增长

---

## 10. 后续可能的功能扩展

| 阶段 | 功能 | 依赖 |
|---|---|---|
| 第一阶段（当前） | 单机开发环境，MATLAB Engine + webwrite 回调 | MATLAB R2024a |
| 第二阶段 | 引擎池支持并发任务 | 多 MATLAB license |
| 第三阶段 | 编译为独立 EXE（MATLAB Compiler），去掉 MATLAB 依赖 | MATLAB Compiler 工具箱 |
| 第四阶段 | 容器化部署（Docker + MATLAB Runtime） | MATLAB Runtime |
| 第五阶段 | 用 Python 重写调度内核，彻底去除 MATLAB 依赖 | 资源充足时 |

当前方案定位在第一阶段，以最小的改动和最大的可靠性为目标。

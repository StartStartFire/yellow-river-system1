# Web 服务开发规范（CLAUDE.md）

## 项目概述

黄河上游**龙羊峡—刘家峡梯级水库多目标优化调度模型**的 Python Web 服务端。

基于 FastAPI 构建，通过 `matlab.engine` 调用 MATLAB 优化模型（NSGA-II / PAEM），提供 HTTP API 和 WebSocket 实时推送。

**当前阶段：原型开发** — 优先保证能运行起来，但代码结构要满足模块化、低耦合、可持续维护、可复用的要求，不为原型期遗留技术债。

---

## 目录结构

```
backend-service/
├── run.py                     # 启动脚本：uvicorn.run("app.main:app")
├── requirements.txt           # Python 依赖清单
├── CLAUDE.md                  # 本文件 — Web 服务开发规范
│
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI 入口 — 只做组装（app 创建 + 生命周期 + 注册路由）
│   ├── config.py              # 全局配置单例（dataclass，所有可变参数收拢到此文件）
│   │
│   ├── api/                   # 路由层 — HTTP 协议适配，不包含业务逻辑
│   │   ├── health.py          # GET /health
│   │   ├── jobs.py            # POST /run, GET /status, /jobs, /results, /process
│   │   ├── ws.py              # WS /ws/{job_id}
│   │   ├── callback.py        # POST /cb（MATLAB 回调入口）
│   │   └── evaluate.py        # POST/GET /evaluate（评价系统）
│   │
│   ├── schemas/               # Pydantic 模型层 — 纯数据定义，零依赖
│   │   ├── job.py             # RunRequest, JobStatusResponse, JobSummary
│   │   ├── result.py          # HealthResponse, ResultResponse
│   │   ├── callback.py        # CallbackPayload, CallbackResponse
│   │   └── evaluate.py        # EvaluateRequest, EvaluateResponse
│   │
│   ├── core/                  # 核心业务逻辑层 — 不知道 HTTP 存在，可脱离 HTTP 测试
│   │   ├── executor.py        # BaseExecutor 抽象基类
│   │   ├── job_manager.py     # JobManager 任务生命周期管理
│   │   ├── callback.py        # CallbackQueue 回调缓冲区 + 信封打包
│   │   └── websocket.py       # ConnectionManager + 广播循环
│   │
│   └── services/              # 外部服务封装层
│       └── matlab.py          # MatlabExecutor — 封装 matlab.engine 调用
│
└── tests/                     # 测试
    └── test_year_range.py     # 年份范围单元测试
```

---

## 层依赖规则（单向依赖）

**严格遵守以下依赖方向，禁止反向引用和循环导入：**

```
main.py
   │
   ├──→ api/*     路由层（HTTP 协议适配）
   │        │
   │        ├──→ schemas/*    Pydantic 模型（零依赖）
   │        │
   │        └──→ core/*       业务逻辑层
   │                 │
   │                 ├──→ schemas/*    （仅 callback.py 引用 CallbackPayload 类型）
   │                 │
   │                 └──→ app.config   （全局配置）
   │
   └──→ services/*   外部服务封装
            │
            ├──→ core/executor    （实现 BaseExecutor 接口）
            ├──→ app.config
            └──→ 外部系统（matlab.engine）
```

### 具体规则

| 禁止的引用 | 原因 |
|-----------|------|
| `api/*` → `main.py` | 路由不可反向引用组装厂 |
| `core/*` → `api/*` | 业务逻辑不可感知 HTTP 层存在 |
| `schemas/*` → `core/*` 或 `api/*` | 数据模型不可依赖业务逻辑 |
| `services/*` → `api/*` 或 `schemas/*` | 外部服务封装只对 core/ 暴露接口 |
| 任何层之间出现循环 import | Python 运行时直接报错 |

---

## 模块职责边界

| 层 | 包含 | 禁止 |
|----|------|------|
| **`app/main.py`** | FastAPI app 创建、lifespan、`include_router`、CORS 中间件 | 定义路由函数、包含业务逻辑 |
| **`app/config.py`** | 所有可变配置参数（dataclass 单例） | 硬编码 IP/端口/路径在业务代码中 |
| **`api/*`** | 路由装饰器、请求解析、调用 core/、序列化响应 | 直接调用 MATLAB Engine、操作数据库、包含业务计算逻辑 |
| **`schemas/*`** | Pydantic 模型定义、字段校验规则 | 任何可执行逻辑（校验器 `@field_validator` 除外） |
| **`core/*`** | 纯业务逻辑、状态管理、数据转换 | 导入 `fastapi`、使用 `Request`/`Response` 对象、抛出 `HTTPException` |
| **`services/*`** | 外部系统调用封装（Engine 启停、命令执行） | 包含业务编排逻辑、直接暴露 HTTP 端点 |
| **`tests/`** | 测试用例、fixture、测试配置 | 生产代码的 import side effect |

---

## Python 代码规范

### 命名风格

| 类别 | 规范 | 示例 |
|------|------|------|
| 模块/文件 | `snake_case` | `job_manager.py`, `callback.py` |
| 类 | `PascalCase` | `class JobManager`, `class TaskConfig` |
| 函数/方法 | `snake_case` | `def submit_task()`, `def _extract_chromosome()` |
| 变量 | `snake_case` | `job_id`, `task_config`, `_executor_ref` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| 私有（模块内） | 前导下划线 | `_build_evaluation_cache()`, `_job_manager` |
| 类型变量 | `T` 或描述性大写 | `T`, `AnyStr` |

### 类型注解

```python
# ✅ 必须：函数参数和返回值标注类型
def submit_task(self, config: TaskConfig) -> JobRecord: ...

# ✅ 必须：类属性标注类型
class JobRecord:
    job_id: str
    status: str  # queued | running | completed | failed

# ✅ 可选：内部变量可从简（原型阶段）
chromo = self._extract_chromosome(result)  # type: list
```

### 异步优先

```python
# ✅ 正确：I/O 操作用 async/await
async def get_status(job_id: str) -> JobStatusResponse: ...

# ✅ 正确：CPU 密集型任务推送到线程池
await self._loop.run_in_executor(self._pool, self._run_optimization_sync, task)

# ❌ 禁止：在异步端点中直接调用阻塞 I/O
# time.sleep(5)  ← 不要这样做
```

### 错误处理

```python
# ✅ 路由层：结构化错误响应
raise HTTPException(status_code=404, detail=f"任务 {job_id} 不存在")

# ✅ core 层：抛业务异常（不涉及 HTTP），由路由层捕获转换
if self._eng is None:
    return TaskResult(success=False, message="Engine 未就绪")

# ✅ 回调路径：静默降级，不传播异常
try:
    await ws.send_json(message)
except Exception:
    disconnected.append(ws)  # 静默清理断开的连接
```

### 导入顺序

按以下分组，每组间空一行，组内按字母序排序：

```python
# 1. Python 标准库
import asyncio
import logging
from abc import ABC, abstractmethod

# 2. 第三方库
from fastapi import APIRouter, HTTPException
import matlab.engine

# 3. 项目内部模块
from app.config import config
from app.core.executor import BaseExecutor, TaskConfig
```

---

## 关键架构模式

### 1. 依赖注入模式

路由模块不直接实例化依赖，而是通过 `init()` 函数由 `main.py` 在 startup 时注入：

```python
# api/jobs.py
_job_manager = None

def init(job_manager) -> None:
    global _job_manager
    _job_manager = job_manager

@router.post("/run")
async def run(req: RunRequest):
    if _job_manager is None:
        raise HTTPException(status_code=503, detail="服务未就绪")
    record = await _job_manager.submit_task(task_config)
    ...
```

```python
# main.py (lifespan)
from app.api import jobs
jobs.init(job_manager)
```

### 2. 策略模式（Executor 抽象）

`BaseExecutor` 定义抽象接口，`MatlabExecutor` 是唯一生产实现：

```
job_manager → BaseExecutor (抽象)
                  └── MatlabExecutor  ← 生产环境，封装 matlab.engine
```

`job_manager` 只依赖 `BaseExecutor` 接口，不感知具体实现。

### 3. 生产者-消费者模式（回调 → WebSocket）

```
MATLAB (webwrite)
    ↓ POST /cb
callback.py 生产者 (CallbackQueue.put)
    ↓ asyncio.Queue
websocket.py 消费者 (broadcast_loop → ConnectionManager.broadcast)
    ↓ ws.send_json
前端客户端
```

`CallbackQueue` 满时自动丢弃最旧消息，确保回调不阻塞 MATLAB 主循环。

### 4. 全局单例模式

| 单例 | 位置 | 用途 |
|------|------|------|
| `config = Config()` | `app/config.py` | 全局配置 |
| `callback_queue = CallbackQueue()` | `app/core/callback.py` | 回调消息缓冲区 |
| `connection_manager = ConnectionManager()` | `app/core/websocket.py` | WS 连接管理 |

单例在各模块内直接 import 使用，不需要通过 main.py 传递。

---

## MATLAB Engine 通信规范

### 线程安全

- MATLAB Engine **非线程安全**，必须串行调用
- `MatlabExecutor` 使用 `ThreadPoolExecutor(max_workers=1)` 确保串行
- 所有 Engine 操作通过 `_run_in_engine_thread()` 桥接到单线程执行

```python
async def _run_in_engine_thread(self, func, *args, **kwargs):
    """在 Engine 专用线程中执行同步函数"""
    return await self._loop.run_in_executor(self._pool, func, *args, **kwargs)
```

### 数据清洗

MATLAB 返回的 `double` 矩阵可能包含 `Inf`/`-Inf`/`NaN`，在进入 Pydantic 序列化前必须清洗：

```python
def _sanitize_matlab_value(value: Any) -> Any:
    if isinstance(value, (int, float)):
        if math.isinf(value) or math.isnan(value):
            return None  # Pydantic 序列化时转为 JSON null
        return value
    return value
```

### 生命周期

```
start()
  ├── eng = start_matlab()
  ├── eng.cd(matlab_root)
  └── eng.load_data()

run(task)  ← 可调用多次，每次按 flag_xixian 重载数据
  ├── eng.load_data()
  ├── eng.eval("global Q_sediment; ...")
  └── eng.nsga_2_para() / PAEM_para()

stop()
  └── eng.quit()
```

---

## 配置管理

### 原则

- 所有可变参数收拢到 `app/config.py` 的 `Config` dataclass
- 业务代码中**不出现硬编码路径、端口、超时**
- 换机器只需改 `matlab_root` 一行

### 当前配置项

```python
@dataclass
class Config:
    host: str = "127.0.0.1"
    port: int = 18080
    cors_origins: list[str] = None  # 默认 localhost:3000/3001
    matlab_root: str = "F:/Model/yellow_river_project/matlab-model"
    data_file: str = "data.xlsx"
    callback_timeout: float = 1.0   # webwrite 超时，单位秒
    default_pop: int = 15
    default_iterate: int = 20
    default_m: int = 2
    default_q_sediment: float = 1800.0
```

访问方式：`from app.config import config` → `config.host`, `config.matlab_root`

---

## 测试策略

| 阶段 | 方法 | 工具 |
|------|------|------|
| 当前（原型） | 手动 curl | `curl` |
| 后续 | 单元测试 + 集成测试 | pytest + httpx |

测试文件放在 `tests/` 目录下，按被测试模块组织：

- `tests/test_year_range.py` → 年份范围功能测试

快速验证脚本请放到根目录 `_sandbox/` 下（已在 `.gitignore`），用完即删。

---

## 常见注意事项

| 事项 | 说明 |
|------|------|
| **MATLAB Engine 线程安全** | 非线程安全，必须串行调用。`MatlabExecutor` 使用 `ThreadPoolExecutor(max_workers=1)` |
| **Python 版本** | 固定 Python 3.11，MATLAB R2024a Engine API 仅支持 3.9~3.11 |
| **虚拟环境** | 使用 venv 或 conda 创建隔离环境，不直接使用全局 Python |
| **`__pycache__`** | Python 字节码缓存，自动生成。已在 `.gitignore` 中忽略 |
| **`webwrite` 超时** | 设置为 1 秒，避免回调阻塞优化主循环 |
| **`numel` Bug** | `numel(A, condition)` 不符合标准 MATLAB 语法，第二个参数被忽略，应改用 `sum(A==0)` |
| **工作目录** | MATLAB Engine 启动后必须 `eng.cd()` 到 `matlab-model/` 目录，否则 `xlsread` 找不到文件 |
| **入口脚本** | 程序入口为 `run.py`，Web 服务通过 `eng.nsga_2_para` 直接调用主循环，不经过 `main.m` |
| **数据加载** | 使用 `load_data.m` 加载 Excel 数据 |
| **内存管理** | 多次优化后 MATLAB 进程内存可能增长，建议定期重启引擎 |
| **回调静默降级** | MATLAB 侧 `webwrite` 失败时 `try-catch` 静默降级，数据通过 JSONL 文件持久化，不影响优化主循环 |

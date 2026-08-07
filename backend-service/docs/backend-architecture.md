# Web 服务后端架构梳理

## 1. 目录结构

```
backend-service/
├── run.py                          # 启动入口
├── requirements.txt                # 依赖
└── app/
    ├── main.py                     # FastAPI 应用实例 + 生命周期（lifespan）
    ├── config.py                   # 全局配置单例（端口、路径、默认参数）
    │
    ├── api/                        # API 路由层 — 只定义路由函数
    │   ├── health.py               # GET /health — 健康检查
    │   ├── jobs.py                 # POST /run, GET /status, /jobs, /results, /process
    │   ├── evaluate.py             # POST /evaluate, GET /evaluate/{job_id}
    │   ├── ws.py                   # WS /ws/{job_id} — WebSocket 推送
    │   └── callback.py             # POST /cb — MATLAB 回调接收
    │
    ├── core/                       # 核心业务层 — 纯逻辑，无路由定义
    │   ├── executor.py             # BaseExecutor 抽象接口 + TaskConfig/TaskResult
    │   ├── job_manager.py          # JobManager 任务队列管理（生命周期 + 串行执行）
    │   ├── callback.py             # CallbackQueue（回调消息缓冲区）
    │   └── websocket.py            # ConnectionManager + broadcast_loop
    │
    ├── schemas/                    # Pydantic 数据模型层
    │   ├── job.py                  # RunRequest, JobStatusResponse, JobSummary
    │   ├── evaluate.py             # EvaluateRequest, EvaluateResponse
    │   ├── result.py               # ResultResponse
    │   └── callback.py             # CallbackPayload, CallbackResponse
    │
    └── services/                   # 服务封装层
        └── matlab.py               # MatlabExecutor（Engine 生命周期管理）
```

### 与旧版扁平结构的区别

旧版 `backend-service/app/` 只有 8 个扁平文件（main.py, models.py, executor.py, matlab_engine.py, job_manager.py, callback.py, websocket.py, config.py），现已重构为四层架构：

| 层 | 职责 | 路由定义？ | 生命周期钩子？ |
|---|------|-----------|--------------|
| `api/` | HTTP/WS 路由函数 | ✅ 是 | ❌ 否 |
| `core/` | 业务逻辑抽象 | ❌ 否 | ❌ 否 |
| `schemas/` | Pydantic 请求/响应模型 | ❌ 否 | ❌ 否 |
| `services/` | 外部服务封装（MATLAB） | ❌ 否 | ✅ 是 |

---

## 2. 模块职责

| 模块（文件） | 职责 | 关键点 |
|-------------|------|--------|
| `main.py` | 应用入口、生命周期、路由注册 | 不定义路由函数；lifespan 管理 executor/job_manager 生命周期 |
| `config.py` | 单例 `Config` dataclass，所有可变参数 | 换机器只改 `matlab_root`；含 CORS origins 配置 |
| `api/health.py` | GET /health 健康检查 | 通过 `init()` 注入 executor 引用 |
| `api/jobs.py` | POST /run, GET /status, /jobs, /results, /process | 通过 `init()` 注入 job_manager 引用 |
| `api/evaluate.py` | POST /evaluate, GET /evaluate/{job_id} | 调用 `evaluation_system` 模块 |
| `api/ws.py` | WS /ws/{job_id} WebSocket 推送 | 通过 `connection_manager` 管理连接 |
| `api/callback.py` | POST /cb MATLAB 回调接收 | Pydantic 校验后入 `CallbackQueue` |
| `core/executor.py` | `BaseExecutor` 抽象基类 + `TaskConfig`/`TaskResult` | 定义执行器抽象接口，MatlabExecutor 实现 |
| `core/job_manager.py` | `JobManager` 任务生命周期：queued→running→completed/failed | `asyncio.Queue` 串行化，后台 worker 消费 |
| `core/callback.py` | `CallbackQueue` — MATLAB 回调的消息缓冲区 | 生产者 MATLAB→/cb，消费者 WS→前端 |
| `core/websocket.py` | `ConnectionManager` — WS 连接分组管理 + `broadcast_loop` | 按 `job_id` 分组广播 |
| `schemas/job.py` | RunRequest, JobStatusResponse, JobSummary Pydantic 模型 | RunRequest 含 13+ 字段 |
| `schemas/evaluate.py` | EvaluateRequest, EvaluateResponse | 评价请求/响应模型 |
| `schemas/result.py` | ResultResponse | 含 chromosome + evaluating 双矩阵 |
| `schemas/callback.py` | CallbackPayload, CallbackResponse | 回调数据校验 |
| `services/matlab.py` | `MatlabExecutor` 实现，封装 `matlab.engine` 调用 | `ThreadPoolExecutor(max_workers=1)` 串行化；约束参数动态注入 |

---

## 3. 数据流转全过程

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────────┐
│  前端     │    │  FastAPI      │    │  JobManager  │    │  MatlabExecutor│
│ (Vue)    │    │  (路由层)     │    │  (调度层)    │    │  (执行层)      │
└────┬─────┘    └──────┬───────┘    └──────┬───────┘    └───────┬────────┘
     │                  │                    │                    │
     │ ① POST /run     │                    │                    │
     │────────────────→│                    │                    │
     │                  │  ② submit_task()  │                    │
     │                  │─────────────────→│                    │
     │                  │                    │  ③ 入队 asyncio.Queue      │
     │                  │                    │  (queued)          │
     │ ④ 返回 job_id   │                    │                    │
     │←────────────────│                    │                    │
     │                  │                    │                    │
     │                  │                    │  ⑤ worker 出队    │
     │                  │                    │  → running         │
     │                  │                    │──────────────────→│
     │                  │                    │  ⑥ eng.eval()     │
     │                  │                    │    load_data()     │
     │                  │                    │    nsga_2_para()   │
     │                  │                    │                    │
     │                  │     ┌─────────┐    │                    │
     │                  │     │ MATLAB   │    │                    │
     │                  │     │ Engine   │    │                    │
     │                  │     └──┬───────┘    │                    │
     │                  │        │            │                    │
     │                  │   ──── ⑦ ──────────│                    │
     │                  │   webwrite POST/cb  │                    │
     │                  │   {iteration, ...}  │                    │
     │   ┌────────┐    │        │            │                    │
     │   │ 前端    │    │   ┌──────────┐     │                    │
     │   │ECharts  │    │   │CallbackQ │     │                    │
     │   │ 实时    │    │   │ asyncio  │     │                    │
     │   │ 渲染    │    │   │ Queue    │     │                    │
     │   └────▲───┘    │   └────┬─────┘     │                    │
     │        │        │        │            │                    │
     │  ⑨ WS 广播     │   ⑧ broadcast      │                    │
     │────────│────────│─── loop 消费 ───────│                    │
     │        │        │        │            │                    │
     │                  │  ⑩ 优化完成        │                    │
     │                  │  ←────────────────│
     │                  │  返回 chromosome   │
     │                  │                    │
```

---

## 4. API 端点汇总

完整 API 文档（含请求/响应示例、字段说明、错误码）见 [api-reference.md](api-reference.md)。

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/run` | 提交优化任务 |
| GET | `/status/{job_id}` | 查询任务状态 |
| GET | `/jobs` | 任务列表 |
| GET | `/results/{job_id}` | 获取优化结果 |
| GET | `/process/{job_id}` | 补拉过程数据 🚧 |
| POST | `/evaluate` | 运行评价算法 |
| GET | `/evaluate/{job_id}` | 获取评价缓存 |
| WS | `/ws/{job_id}` | 实时进度推送 |
| POST | `/cb` | MATLAB 回调接收 |

---

## 5. POST /run 执行过程（核心流程）

```
前端 POST /run
  │
  ▼
jobs.py:run()                          ← 路由层
  │ 解析 RunRequest → TaskConfig
  │
  ▼
job_manager.submit_task(config)         ← 调度层
  │ ① 生成 uuid → JobRecord(job_id, config)
  │ ② Record 入队 _queue.put_nowait()
  │ ③ 立即返回 Record（此时 status=queued）
  │
  ▼
后台 worker 协程 (_worker_loop)         ← 异步消费
  │ ① 出队 _queue.get()（阻塞，直到有任务）
  │ ② JobRecord.status = "running"
  │ ③ _current_job_id = record.job_id
  │
  ▼
executor.run(task_config)               ← 执行层
  │
  ▼
MatlabExecutor._run_optimization_sync() ← 在 ThreadPoolExecutor 线程中
  │
  ├─ ① eng.load_data()                重载数据（西线调水方案）
  ├─ ② eng.eval() 设置全局变量
  │    - Q_sediment                    调沙流量
  │    - LONG_Z_INI_VAL                龙羊峡起调水位（可选）
  │    - LIU_Z_INI_VAL                 刘家峡起调水位（可选）
  │    - QMIN_VAL                      防凌流量（可选）
  │
  ├─ ③ eng.nsga_2_para() 或 PAEM_para()
  │    ↓
  │    MATLAB 内部循环（iterate 代）       ← 每次迭代回调
  │    ├─ write_json_log(...)          写入 JSONL 文件
  │    ├─ http_callback_push.m          → 每 10 代 POST /cb
  │    │    webwrite(POST /cb, {type:"progress", ...})
  │    │    ↓
  │    │    callback.py:POST /cb        ← 路由层
  │    │    → CallbackQueue.put()       消息入队
  │    │    → broadcast_loop 消费        → WS /ws/{job_id}
  │    │                                   → 前端 ECharts 实时更新
  │    └─ ... 继续进化
  │
  └─ ④ 返回结果（chromosome + evaluating 矩阵）
  │
  ▼
job_manager 处理完成
  ├─ JobRecord.result = TaskResult
  ├─ JobRecord.status = "completed"
  ├─ _current_job_id = null
  ├─ 最后一次过程数据通过 CallbackQueue 推送完成 →
  │
  ▼
前端可轮询 GET /results/{job_id} 获取最终结果
```

---

## 6. POST /evaluate 执行过程

```
前端 POST /evaluate
  │
  ▼
evaluate.py:evaluate_job()
  │
  ├─ ① 验证 job_id 存在且 completed
  │
  ├─ ② 调用 evaluation_system
  │    ├─ run_complete_evaluation("ALL")
  │    │   ├─ NMFAlgorithm
  │    │   ├─ PPAlgorithm
  │    │   ├─ AHP_FUZZYAlgorithm
  │    │   └─ RankSumTheory.rank_sum_integrate()
  │    └─ → algorithm_results + integrated_results
  │
  └─ ③ _build_evaluation_cache()
       ├─ convergence             收敛曲线 {NMF: [...], PP: [...]}
       ├─ rankings                NMF/PP/AHP_FUZZY 得分 + ALL 整合排名
       ├─ radar                   算法得分雷达图（3 个算法 × 10 方案）
       └─ raw_indicators          R1~R22 原始指标（10 方案 × 22 指标）
```

---

## 7. 关键设计决策

| 决策 | 原因 | 实现方式 |
|------|------|----------|
| **MATLAB Engine 串行** | 非线程安全 | `ThreadPoolExecutor(max_workers=1)` |
| **任务串行执行** | Engine 进程内状态（数据、变量）共享 | `asyncio.Queue` + 后台 worker |
| **回调静默降级** | Web 故障不影响 MATLAB 模型 | `http_callback_push.m` 中 try-catch + Timeout=1s |
| **数据持久化** | 服务重启后任务数据不丢失 | JSONL 文件 + 内存 JobRecord |
| **WebSocket 广播** | 实时推送优化进度 | `CallbackQueue`(asyncio.Queue) + `broadcast_loop` |
| **约束参数注入** | 不改 MATLAB 核心逻辑，运行时动态传参 | `eng.eval("global QMIN_VAL; ...")` 全局变量 |
| **Pydantic 校验** | 保证 API 请求/响应符合类型契约 | `RunRequest`/`EvaluateResponse` 等 schema |

---

## 8. 数据流补充说明

### 回调推送（MATLAB → 前端）

```
MATLAB 每 10 代
  → http_callback_push.m
    → webwrite /cb  (POST, Timeout=1s)
      → callback.py:POST /cb
        → CallbackQueue.put(envelope)
          → broadcast_loop (后台协程)
            → ConnectionManager.broadcast(job_id, envelope)
              → ws.send_json(envelope)  (对所有订阅该 job 的客户端)
```

### 评价系统数据流（evaluation_system → API）

```
evaluation_system (Python 独立模块)
  → run_complete_evaluation(data_matrix)
    → NMF / PP / AHP_FUZZY 算法
    → RankSumTheory 整合
  → algorithm_results
  → integrated_results
    ↓
_build_evaluation_cache()
  → rankings[]       → 排名表格
  → radar            → 算法得分雷达图
  → convergence      → 收敛曲线
  → raw_indicators   → 桑基图（R1~R22 原始指标）
    ↓
缓存到 JobRecord.evaluation_result
  → GET /evaluate/{job_id} 读取
```

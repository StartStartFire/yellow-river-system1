# 后端架构与设计决策

> **定位（与 api-reference.md 的分工）**：接口契约（端点/请求响应/字段）见 [api-reference.md](api-reference.md)；本文件只记**代码里读不出的东西**——两条核心执行链路与"为什么这样设计"。
> 目录结构、模块职责、端点清单均以代码为准（从 `app/main.py` 与 `app/api/` 可读），不再复制。

***

## 1. 分层（一句话）

`api/`（路由）→ `core/`（任务队列/回调缓冲/WS 管理）→ `schemas/`（Pydantic 契约）→ `services/`（MATLAB Engine 封装）。lifespan 中初始化 executor/job\_manager 并 `init()` 注入各路由模块，广播协程 `broadcast_loop` 常驻后台。

***

## 2. POST /run 执行链路

```
jobs.py:run() 解析 RunRequest → TaskConfig（含算法/参数/约束/年份范围）
  → JobManager.submit_task()：生成 UUID → JobRecord 入 asyncio.Queue → 立即返回 queued
  → 后台 worker 出队 → status=running
  → MatlabExecutor._run_optimization_sync()（专用单线程 ThreadPoolExecutor 内）
      ① eng.eval 设置 YEAR_START / YEAR_END（可选，供 load_data 截取年份）
      ② eng.load_data(data_file, flag_xixian)  按西线调水方案重载数据
      ③ eng.eval 注入 Q_sediment / LONG_Z_INI_VAL / LIU_Z_INI_VAL / QMIN_VAL（可选）
      ④ eng.nsga_2_para(pop, iterate, M, Q_sediment, Pc) 或 eng.PAEM_para(...)
           内部：每代 write_json_log → NSGA2_progress.jsonl
                 每 10 代 push_callback_data.m → http_callback_push.m → POST /cb
                     → CallbackQueue → broadcast_loop → WS /ws/{job_id} → 前端
      ⑤ 返回 (chromosome, evaluating, plan_details)（Inf/NaN 清洗为 null）
  → JobRecord.result / status=completed（失败则 failed + message）
```

***

## 3. POST /evaluate 执行链路

```
evaluate.py:evaluate_job() 校验 job 存在且 completed、存在 evaluating 矩阵
  → 动态注入 evaluation-model 到 sys.path（import matplotlib Agg 后端）
  → 方法 = ALL：run_complete_evaluation(data_source=矩阵, config_dict=静默配置)
           = 单算法：run_single_algorithm(...)
  → _build_evaluation_cache() 聚合为前端结构：
       convergence（NMF/PP 收敛曲线）、rankings（三算法 + ALL 整合排名）、
       radar（算法得分雷达图，前 10 方案）、raw_indicators（前 10 方案 22 项原始指标）
  → 存 JobRecord.evaluation_result（后续 GET /evaluate/{job_id} 读缓存，
     另一端 GET /decision/{job_id} 用其 ALL 排名给方案排序）
```

***

## 4. 关键设计决策（为什么）

| 决策               | 原因                                                                           |
| ---------------- | ---------------------------------------------------------------------------- |
| MATLAB Engine 串行 | 非线程安全 → `ThreadPoolExecutor(max_workers=1)`                                  |
| 任务队列串行执行         | Engine 进程内全局变量（数据、约束）共享，不能并发跑两个任务 → `asyncio.Queue` + 单 worker               |
| 回调静默降级           | Web 服务故障不能影响 MATLAB 模型 → 回调 `try-catch` + `Timeout=1s`，数据仍由 JSONL 持久化        |
| 约束参数动态注入         | 不改 MATLAB 核心逻辑 → `eng.eval("global QMIN_VAL; ...")`，起调水位/防凌流量/年份范围由 API 传入   |
| WS 广播而非轮询        | 前端实时性 → `CallbackQueue` + 常驻 `broadcast_loop`；补拉由 `GET /process/{job_id}` 兜底 |
| 求值结果缓存           | 重复 GET 不重算评价 → `JobRecord.evaluation_result`                                 |
| Pydantic 双端校验    | 请求/响应与回调数据统一契约 → `schemas/` 一层                                               |

***

## 5. 已知边界

- **内存态存储**：任务记录在进程内存，服务重启即丢失（JSONL 文件仍在，但 JobRecord 不可恢复）；多次优化后 MATLAB 进程内存增长，建议定期重启 Engine

- **plan\_details 兼容**：旧版模型运行的任务无 plan\_details，`GET /decision` 返回 `plans: []` + 提示

- **process\_data 仅存最新一份**：`JobRecord.process_data` 只保留最近一次推送，不累积


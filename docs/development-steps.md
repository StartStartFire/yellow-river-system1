# 开发步骤流程

> 当前阶段：**功能扩展（原型已全部完成）**
> 目标：Web 服务骨架搭建完成，全链路可运行，为后续扩展打好模块化基础
>
> ✅ **原型 6 步已全部完成**（详见下方状态标记）
> 当前重点参见 [model-run-integration.md](model-run-integration.md)（前后联调）和 [process-transparent-plan.md](process-transparent-plan.md)（过程透明化）

---

## 总体步骤图

原型阶段的开发分为 6 步，每步完成后进入下一步，不可跳跃：

```
Step 1: Web 服务骨架
   └─ 验证: GET /health 返回 ok
         ↓
Step 2: 任务生命周期（无 MATLAB）
   └─ 验证: POST /run → status 迁移正常
         ↓
Step 3: MATLAB Engine 集成
   └─ 验证: 后台线程成功调用 eng.nsga_2_para
         ↓
Step 4: WebSocket + /cb 端点（接收侧）
   └─ 验证: curl POST /cb → WS 客户端收到广播
         ↓
Step 5: MATLAB 回调推送（发送侧）
   └─ 验证: MATLAB 运行中向 /cb 发送 POST 并入库
         ↓
Step 6: 结果查询 + 全链路联调
   └─ 验证: POST→WS→GET 端到端通过
```

---

## ✅ Step 1：Web 服务骨架

**目标**：创建 `backend-service/` 目录结构，定义数据模型，验证服务启动正常。

### 虚拟环境（首次搭建前执行）

```bash
cd F:\Model\yellow_river_project\backend-service

# 方式一：venv（推荐，轻量）
python -m venv .venv
.venv\Scripts\activate      # Windows PowerShell: .venv\Scripts\Activate.ps1

# 方式二：conda
conda create -n yellow-river-web python=3.11 -y
conda activate yellow-river-web

# 安装依赖
pip install -r requirements.txt
```

> Python 版本必须为 3.11（MATLAB R2024a Engine API 兼容范围 3.9~3.11）。
> 虚拟环境目录 `.venv/` 或 conda 环境不提交到 git。

### 新建文件清单（注：原型 Step 1 采用扁平结构，后续已重构为 api/core/schemas/services 四层架构）

| 文件 | 内容 |
|------|------|
| `backend-service/requirements.txt` | FastAPI, uvicorn, pydantic, websockets（Python 3.11） |
| `backend-service/run.py` | uvicorn 启动入口 |
| `backend-service/app/__init__.py` | 空包文件 |
| `backend-service/app/config.py` | Config dataclass 全局单例 |
| `backend-service/app/models.py` | 所有 Pydantic 模型 |
| `backend-service/app/executor.py` | BaseExecutor 抽象 |
| `backend-service/app/main.py` | FastAPI app + /health 端点 |
| `backend-service/app/matlab_engine.py` | 空桩文件 |
| `backend-service/app/job_manager.py` | 空桩文件 |
| `backend-service/app/callback.py` | 空桩文件 |
| `backend-service/app/websocket.py` | 空桩文件 |

### Pydantic 模型

模型中定义了 `RunRequest`、`JobStatusResponse`、`HealthResponse`、`CallbackPayload`、`CallbackResponse`，详细代码见 [`technical-roadmap.md` 第 6.4 节](technical-roadmap.md#64-回调数据格式与校验pydantic-模型)。核心清单见下表：

| 模型 | 用途 | 关键字段 |
|------|------|---------|
| `RunRequest` | POST /run 请求体 | algorithm, pop, iterate, M, Q_sediment, K_mut |
| `JobStatusResponse` | GET /status/{id} 响应 | job_id, status, progress_percent, created_at |
| `HealthResponse` | GET /health 响应 | status, engine, version |
| `CallbackPayload` | POST /cb 请求体 | type ('progress'), data (dict) |
| `CallbackResponse` | POST /cb 响应 | received, job_id |

### 配置（config.py）

```python
from dataclasses import dataclass

@dataclass
class Config:
    """所有可变参数收拢到此类。

    详细代码见 technical-roadmap.md 第 6.1 节。
    换机器只需改 matlab_root 一行。
    """
    host: str = "127.0.0.1"
    port: int = 18080
    matlab_root: str = "F:/Model/yellow_river_project/matlab-model"
    data_file: str = "data.xlsx"
    flag_xixian: str = "全无"
    callback_host: str = "127.0.0.1"
    callback_port: int = 18080
    callback_timeout: float = 1.0
    default_pop: int = 15
    default_iterate: int = 20
    default_m: int = 2
    default_q_sediment: float = 1800.0
    default_k_mut: int = 50

    @property
    def callback_url(self) -> str:
        return f"http://{self.callback_host}:{self.callback_port}/cb"

config = Config()
```

> 完整字段说明见 `technical-roadmap.md` 第 6.1 节「配置模型」。

### 验证

```bash
cd backend-service
python -m app.main
# 新开终端:
curl http://127.0.0.1:18080/health
# 预期: {"status":"ok","engine":"not started","version":"1.0.0"}
```

---

## ✅ Step 2：任务生命周期管理

**目标**：不依赖 MATLAB，用 MockExecutor 跑通任务队列和状态迁移。

### 改动文件

| 文件 | 操作 |
|------|------|
| `executor.py` | 实现 `BaseExecutor` + `TaskConfig` |
| `job_manager.py` | 实现 `JobManager`（队列 + 状态机） |
| `main.py` | 注册 `/run`、`/status/{id}`、`/jobs` 端点 |

### executor 参数类型

`BaseExecutor.run()` 接收 `TaskConfig` 而非 `RunRequest`，`job_manager` 内部从请求体做转换：

```python
# executor.py
from dataclasses import dataclass

@dataclass
class TaskConfig:
    algorithm: str                # 'nsga2' | 'paem'
    pop: int
    iterate: int
    M: int
    Q_sediment: float
    K_mut: int | None = None     # PAEM 专用
```

### 验证

```bash
# 提交任务
curl -X POST http://127.0.0.1:18080/run \
  -H "Content-Type: application/json" \
  -d '{"algorithm":"nsga2","pop":15,"iterate":20}'
# 预期: {"job_id":"...","status":"queued"}

# 轮询状态
curl http://127.0.0.1:18080/status/{job_id}
# 预期: status 最终变为 "completed"

# 任务列表
curl http://127.0.0.1:18080/jobs
# 预期: 含刚完成的任务
```

---

## ✅ Step 3：MATLAB Engine 集成

**目标**：用真实 MATLAB Engine 替换 MockExecutor，跑通一次 nsga_2_para 调用。

### 前置条件

- MATLAB R2024a 已安装
- Python 3.11 已安装 `matlab.engine`（在 MATLAB 目录 `python -m pip install .`）
- `data.xlsx` 存在于 `config.matlab_root` 目录

### 改动文件

| 文件 | 操作 |
|------|------|
| `matlab_engine.py` | 实现 `MatlabExecutor`（继承 BaseExecutor） |
| `main.py` | 将 executor 替换为 `MatlabExecutor(config)` |
| `config.py` | 确认路径配置正确 |

### Engine API 注意事项

- `eng.cd(config.matlab_root)` 必须在首次调用前执行
- `eng.load_data('data.xlsx', '全无')` 加载全局变量
- `eng.nsga_2_para(pop, iterate, M, Q_sediment, nargout=1)` 串行调用
- Engine 非线程安全，需用 `ThreadPoolExecutor(max_workers=1)`

### 验证

```bash
# 提交任务，status 应经历 queued → running → completed
curl -X POST http://127.0.0.1:18080/run \
  -H "Content-Type: application/json" \
  -d '{"algorithm":"nsga2"}'
```

---

## ✅ Step 4：WebSocket + /cb 端点

**目标**：实现实时推送通道的接收侧，HTTP POST 到 `/cb` 后 WebSocket 客户端能收到广播。

### 改动文件

| 文件 | 操作 |
|------|------|
| `callback.py` | 实现 `/cb` 端点，Pydantic 校验后写入 asyncio.Queue |
| `websocket.py` | 实现连接管理 + 从 Queue 消费并广播 |
| `main.py` | 注册 `/cb`、`/ws/{job_id}` 端点，启动后台广播协程 |

### WebSocket 消息格式

```json
{
  "type": "progress",
  "job_id": "uuid",
  "timestamp": "2026-07-11 14:30:00",
  "payload": {
    "iteration": 5,
    "total_iterations": 20,
    "progress_percent": 25.0,
    "objective_values": [[12.3, 45.6]],
    "algorithm": "nsga2"
  }
}
```

### 验证

```bash
# 方式一: 使用 websocat 或 wscat 连接
# 终端 1: wscat -c ws://127.0.0.1:18080/ws/test-job
# 终端 2:
curl -X POST http://127.0.0.1:18080/cb \
  -H "Content-Type: application/json" \
  -d '{"type":"progress","data":{"iteration":1,"timestamp":"...","objective_values":[[10,20]],"progress_percent":5.0}}'
# 终端 1 应收到广播消息
```

---

## ✅ Step 5：MATLAB 回调推送

**目标**：MATLAB 每代进化结束时向 Web 服务推送进度。

### 新增文件

| 位置 | 文件 | 内容 |
|------|------|------|
| `matlab-model/` | `http_callback_push.m` | HTTP POST 回调推送函数 |
| `matlab-model/` | `callback_config.txt` | 内容: `http://127.0.0.1:18080/cb` |

### 修改文件

| 文件 | 修改位置 |
|------|---------|
| `matlab-model/nsga_2_para.m` | `write_json_log(json_data, json_fid);` 之后插入一行 |
| `matlab-model/PAEM_para.m` | `write_json_log(json_data, log_fid, false, true);` 之后插入一行 |

插入内容：

```matlab
    http_callback_push('progress', json_data);  % 第 5 步新增
```

### 不改动的文件

- `evaluate_objective.m` / `evaluate_objective_NSGA2.m` / `evaluate_objective_PAEM.m` — 纯计算，不参与推送
- `load_data.m` / `initialize_population.m` / `write_json_log.m` — 逻辑不变
- `main.m` — 仅命令行入口

### 验证

启动 Web 服务后，手动或通过测试脚本触发 MATLAB 优化，观察 `/cb` 端点的接收日志和 WebSocket 广播。

---

## ✅ Step 6：结果查询 + 全链路联调

**目标**：实现结果查询端点，完成端到端验证。

### 改动文件

| 文件 | 操作 |
|------|------|
| `main.py` | 注册 `GET /results/{job_id}` 端点，从 JSONL 文件读取最终代数据 |

### 验证全链路

```bash
# 1. 提交任务
JOB_ID=$(curl -s -X POST http://127.0.0.1:18080/run \
  -H "Content-Type: application/json" \
  -d '{"algorithm":"nsga2"}' | python -c "import sys,json;print(json.load(sys.stdin)['job_id'])")

# 2. WebSocket 实时接收进度（新终端）
wscat -c "ws://127.0.0.1:18080/ws/$JOB_ID"

# 3. 任务完成后查询结果
curl "http://127.0.0.1:18080/results/$JOB_ID"
# 预期返回:
# {
#   "job_id": "...",
#   "status": "completed",
#   "chromosome": [[...]],  # Pareto 解集，pop × (V+M+2) 矩阵
#   "objective_names": ["f1_缺水", "f2_发电"],
#   "generated_at": "2026-07-11 14:30:00"
# }
```

### 结果格式说明

`GET /results/{job_id}` 返回的 `chromosome` 矩阵每行包含：

| 列范围 | 内容 |
|-------|------|
| 1 ~ V | 决策变量（龙羊峡 + 刘家峡逐时段水位） |
| V+1 ~ V+M | 目标函数值 |
| V+M+1 | 非支配排序等级 |
| V+M+2 | 拥挤距离 |

V = 20 × Y × 2（当前 Y=54，故 V=2160）。

---

## 编码建议

### 每一步开始前

1. 阅读 `technical-roadmap.md` 中对应步骤的详细设计
2. 确认所有前置步骤已完成
3. 检查当前代码是否与目标步骤一致

### 每一步完成后

1. 运行该步骤的验证命令，确认通过
2. 更新 `work-log.md`（新增一条，删除最旧的一条，保持最多 3 条）
3. 如果发现设计需要调整，先在 `technical-roadmap.md` 中更新再改代码

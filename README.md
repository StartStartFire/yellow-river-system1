# 黄河上游龙羊峡—刘家峡梯级水库多目标优化调度模型

## 项目概述

本系统基于 **NSGA-II / PAEM** 多目标遗传算法，对黄河上游龙羊峡—刘家峡梯级水库群进行多目标优化调度，提供 **FastAPI Web 服务** + **Vue3 前端** 的完整交互平台。

### 四端架构

| 模块 | 路径 | 技术栈 | 职责 |
|------|------|--------|------|
| **模型** | `matlab-model/` | MATLAB (R2024a) | NSGA-II / PAEM 多目标优化调度核心算法 |
| **后端** | `backend-service/` | Python 3.11 + FastAPI | HTTP API + WebSocket + MATLAB Engine 桥接 |
| **评价** | `evaluation-model/` | Python 3.11 | NMF / PP / AHP-FUZZY 多算法评价决策 |
| **前端** | `frontend-service/` | Vue 3 + TypeScript + Vite | 可视化交互界面 |

---

## 环境搭建（全新机器）

### 1. 安装前置依赖

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| Python | **3.11.9** | MATLAB R2024a Engine API 仅支持 Python 3.9~3.11 |
| Conda | 任意 | 推荐 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) |
| MATLAB | **R2024a** | 用于运行优化模型（含 MATLAB Engine API） |
| Node.js | >=18 | 用于运行前端 |

> **注意**：如果 MATLAB 安装目录下的 Engine API 尚未注册到 Python，需手动安装：
> ```bash
> cd "C:\Program Files\MATLAB\R2024a\extern\engines\python"
> python setup.py install
> ```

### 2. 克隆项目

```bash
git clone <仓库地址> E:\model\yellow_river_project
cd E:\model\yellow_river_project
```

### 3. 创建 Conda 环境

```bash
# 通过 environment.yml 创建（自动安装 requirements.txt 中的依赖）
conda env create -f environment.yml

# 激活环境
conda activate yellow-river-web

# 验证关键依赖已安装
python -c "import fastapi; print(fastapi.__version__)"
```

### 4. 启动 Backend 服务

```bash
# 确保 conda 环境已激活
conda activate yellow-river-web

# 启动服务（自动热重载）
cd backend-service
python run.py
```

服务启动在 `http://127.0.0.1:18080`。

验证健康检查：

```bash
curl http://127.0.0.1:18080/health
# 预期返回: {"status":"ok","engine":"ready"}
```

### 5. 启动 Frontend 服务（可选）

```bash
cd frontend-service
npm install
npm run dev
```

前端运行在 `http://localhost:3000`。

---

## 快速验证

### 提交一个优化任务

```bash
curl -X POST http://127.0.0.1:18080/run \
  -H "Content-Type: application/json" \
  -d '{"algorithm":"nsga2","pop":15,"iterate":5,"M":2,"Q_sediment":1800}'
```

记录返回的 `job_id`，轮询状态：

```bash
curl http://127.0.0.1:18080/status/<job_id>
```

---

## 项目目录结构

```
E:\model\yellow_river_project\
├── matlab-model/           # MATLAB 优化模型
│   ├── nsga_2_para.m       # NSGA-II 主循环
│   ├── PAEM_para.m         # PAEM 主循环
│   ├── evaluate_objective*.m  # 目标函数评估
│   ├── load_data.m         # 数据加载（Excel → 全局变量）
│   ├── data.xlsx           # 输入数据（18 个 sheet）
│   ├── http_callback_push.m # HTTP 回调推送
│   ├── push_callback_data.m # 回调数据统一封装（progress + process_data）
│   └── docs/               # 模型专属文档
│
├── backend-service/        # Python FastAPI Web 服务
│   ├── run.py              # 启动入口
│   ├── requirements.txt    # Python 依赖清单
│   ├── app/
│   │   ├── api/            # 路由层（5 个路由器）
│   │   ├── core/           # 业务核心（任务管理、回调、WebSocket）
│   │   ├── schemas/        # Pydantic 数据模型
│   │   └── services/       # MATLAB Engine 生命周期管理
│   └── docs/               # 后端专属文档
│
├── evaluation-model/       # Python 评价系统
│   ├── evaluation_system/  # NMF / PP / AHP-FUZZY 算法
│   └── docs/               # 评价系统文档
│
├── frontend-service/       # Vue3 + TypeScript 前端
│   ├── src/
│   │   ├── views/          # 13 个页面视图
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── components/     # 35+ 组件
│   │   ├── mock/           # Mock 数据
│   │   └── types/          # TypeScript 类型
│   └── docs/               # 前端文档
│
├── docs/                   # 跨项目文档
├── environment.yml         # Conda 环境定义
├── CLAUDE.md               # 项目开发规范
└── README.md               # 本文件
```

---

## 配置说明

**`backend-service/app/config.py`** 是唯一配置入口。`matlab_root` 自动基于项目根目录计算，**换机器无需修改路径**。

如需调整，可修改 `config.py` 中的以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `host` / `port` | `0.0.0.0:18080` | 服务监听地址（本机访问 `http://127.0.0.1:18080`） |
| `callback_timeout` | `1.0` | MATLAB 回调 HTTP 超时（秒） |
| `default_pop` | `15` | 默认种群规模 |
| `default_iterate` | `20` | 默认迭代代数 |

---

## 常见问题

**Q: 启动后 `health` 返回 `engine:starting`？**
A: MATLAB Engine 首次启动约需 10~30 秒，等待自动重试即可。

**Q: 运行时提示找不到 `matlab.engine`？**
A: 确保已安装 MATLAB Engine API for Python，参考上方"安装前置依赖"。

**Q: 前端页面空白或 API 调用失败？**
A: 检查后端是否在 `18080` 端口运行。CORS 默认放行所有来源（`config.py` 中 `cors_origins = ["*"]`，内网调试用），如需收紧可改为前端地址白名单。

---

## 技术文档索引

| 文档 | 路径 | 内容 |
|------|------|------|
| API 参考 | `backend-service/docs/api-reference.md` | 所有 HTTP/WS 端点说明 |
| 后端架构 | `backend-service/docs/backend-architecture.md` | 四层架构设计 |
| 模型规格 | `matlab-model/docs/model-specification.md` | 目标函数、约束条件 |
| 调度规则 | `matlab-model/docs/scheduling-rules.md` | 12 条调度规则 |
| 评价数据规格 | `evaluation-model/docs/evaluation-data-specification.md` | 评价系统输入输出定义 |
| 评价模型与算法 | `docs/evaluation-model-and-algorithm.md` | 论文用：指标体系、NMF/PP/AHP-Fuzzy/序号总和原理与运行环境 |
| 项目目录导航 | `docs/project-nav.md` | 四端目录结构与职责总览 |
| AI 工作日志 | `docs/work-log.md` | 完成任务记录 |

# 水沙耦合仿真模型接入系统 — 部署与拆分文档

> 本文档记录"水沙统一调度 + 河道水文水动力演变 + 输沙造床时空耦合模型"（Python，西安理工大学）
> 接入黄河上游水库群多目标调度系统的**完整部署过程**与**模型拆分/服务化方法**。
> 适用于后续维护、复现、二次开发。

---

## 1. 概述

### 1.1 模型来源与定位
- **模型名称**：水沙统一调度模型与河道水文水动力演变、输沙造床的时空耦合模型
- **开发单位**：西安理工大学
- **编写语言**：Python 3.11，依赖 numpy / pandas / scipy / sklearn / matplotlib / openpyxl
- **输入**：设计洪水重现期（2 / 5 / 10 / 50 / 100 年）+ 水库初始水位（可选）
- **输出**：各断面洪水过程、刘家峡下泄—兰州断面流量的迭代收敛过程、包头—头道拐河段冲淤量、龙羊峡调度过程

### 1.2 与原系统模型（NSGA-II / PAEM）的差异（关键）
| 维度 | 原模型（matlab-model） | 水沙耦合模型（river_model） |
|------|------------------------|------------------------------|
| 语言 | MATLAB | Python |
| 性质 | **多目标优化**（Pareto 解集） | **确定性仿真**（给定洪水→一套结果） |
| 求解 | NSGA-II / PAEM 遗传算法 | 马斯京根洪水演进 + **自迭代试算**（非遗传算法） |
| 评价 | NMF/PP/AHP-FUZZY 排名 Pareto 解集 | **无** evaluating 矩阵，不参与多算法评价 |
| 目标 | 缺水量/发电量/协同度 | 兰州断面流量落入控制区间 + 冲淤量 |

> 因此接入后系统新增一条"**洪水情景仿真 + 过程透明**"链路，与原有"多目标优化 + 评价决策"并存；评价决策页对水沙任务需**优雅降级**。

---

## 2. 模型拆分方法

拆分目标：**开展模型透明化集成，实现"模型拆分、接口定义、服务封装"**，让每个子模块可独立调用、能暴露过程数据。

### 2.1 拆分粒度（先粗后细）
按模型的**自然计算阶段**（即理论给出的三个子模型）拆分：

| 模块 | 对应 coupledModel.py | 作用 | 是否独立 |
|------|---------------------|------|----------|
| **M1 水沙调度** | `run_real_time_scheduling` (257 行) | 逐日推演各库，输出刘家峡下泄、各库水位/出力/下泄/弃水 | ⚠️ 全局状态重 |
| **M2 洪水演进** | `calculate_nonlinear_coefficients`(1221) + 8×`muskingum_nonlinear_*`(1250–1400) | 上断面下泄 + 支流来水 → 演进 → 8 断面洪水过程 | ✅ 纯 numpy |
| **M3 输沙造床** | `run_sediment_model`(2014) | 包头/头道拐流量 → 各河段冲淤 + 平滩流量更新 | ✅ 较易 |
| **C 耦合编排** | `adjust_liujiaxia_discharge`(1457) + `run_real_time_scheduling_for_single_step`(1480) | 调度→演进→兰州达标→修正下泄→再调度（自迭代闭环） | 编排层 |

> **只拆成"模块级"接口，不拆"过程数据级"**：8 个断面、滩地/主槽、子河段等属于**过程数据**（M2/M3 返回 dict 即可），不要给每个断面单独一个接口，避免过度拆分。

> **接入现状（重要）**：
> - **M2 洪水演进**：已**真正接入运行链路**——`run_model_service.py` 调用 `mod_routing.run_routing()` 产出 8 断面结果，并与 `coupledModel` 内部演进结果做一致性校验（`m2_consistency_max_diff` 字段），实测**逐点差值为 0.0**；单元验证见 `river_model/tests/test_mod_routing.py`（独立运行 2 ms 复现结果）。
> - **M3 输沙造床**：已接入（`run_model_service.py` 调用 `mod_sediment.run_sediment()`）。
> - **M1 水沙调度**：状态耦合强，采用**适配器模式**服务化——`mod_scheduling.extract_scheduling()` 统一抽取 6 库调度结果（水位/出力/入库/出库/弃水）；单元验证见 `river_model/tests/test_mod_scheduling.py`。
> - **C 耦合编排**：仍随 `coupledModel` 自迭代闭环运行，为整包计算。

### 2.2 接口定义（已完成）

**M2 洪水演进** `river_model/mod_routing.py`
```python
run_routing(liujiaxia_outflow, mh_flow=None, xt_flow=None, params=None) -> dict
# 返回 { "兰州","下河沿","青铜峡","石嘴山","巴彦高勒","三湖河口","包头","头道拐": list }
```

**M3 输沙造床** `river_model/mod_sediment.py`
```python
run_sediment(Q_baotou, Q_toudaoguai, base_xlsx=None, save_output=False, output_dir=None, label="", quiet=False) -> dict
# 返回 { "segments":[{段号,段长(km),总冲淤量(m³)}], "total", "reach":{in,out}, "n_segments", "n_time" }
```

**C 耦合编排（服务入口）** `river_model/run_model_service.py`
```python
# 命令行：python run_model_service.py --flood_frequency 2年 --job_id X [--cb_url ...] [--result_file ...]
# 内部顺序：M1 调度 → M2 演进 → 判断兰州达标 → 调整刘家峡下泄 → 重算（M1/M2）→ ... → M3 冲淤
```

### 2.3 服务化要点
- 把 `coupledModel.py` 的顶层脚本（"导入即运行 + input() + 相对路径 + 全局状态 + matplotlib"）改造为**可传参、可返回结构化结果、可上报进度**的服务。
- **路径收拢**：所有 `./xxx` 改为基于 `os.path.dirname(__file__)` 的绝对路径，消除 cwd 依赖。
- **隐藏 GUI**:`matplotlib.use('Agg')` + 屏蔽 `plt.show()`；`print` 用 `quiet` 门控。
- **进度上报钩子**（仿 MATLAB 的 `http_callback_push.m`，唯一侵入点）：
  ```python
  def _cb_push(data_type, data):   # 仅当设置 RIVER_CB_URL 时启用；失败静默降级
      requests.post(RIVER_CB_URL, json={"type": data_type, "data": data}, timeout=1)
  ```
  在反馈迭代循环中推送：`type='progress'`（迭代号/最大偏差/进度）+ `type='process_data'`（本轮刘家峡下泄、兰州断面流量）；结束时推送完整结果（含 sections/iteration_history/reservoir/sediment）。

---

## 3. 部署到系统的完整过程

数据流总览：

```
前端(模型配置→调水调沙→重现期) --POST /run{algorithm:"water_sediment", flood_frequency}--> JobManager
  → 按算法路由到 WaterSedimentExecutor（子进程）
       python run_model_service.py --flood_frequency X --job_id Y --cb_url .../cb --result_file ...json
         run_coupled: M1调度→M2演进→反馈迭代→M3冲淤
         每次迭代 POST /cb {type:'progress'/'process_data', data:{job_id, ...}}
            ↓
       /cb 按 data.job_id 路由 → callback_queue → broadcast_loop → WS → 前端过程透明页
         结束 → 结果 dict 写 result_file → executor 读取 → TaskResult → completed
  → GET /process/{job_id}（补拉）+ GET /results/{job_id}（result 字段）
```

### 3.1 模型侧改造
| 文件 | 改动 |
|------|------|
| `river_model/mod_routing.py` | 新增（M2 拆分模块，纯函数） |
| `river_model/mod_sediment.py` | 新增（M3 拆分模块） |
| `river_model/run_model_service.py` | 新增（子进程服务入口 + 结果 JSON + 进度上报） |
| `river_model/coupledModel.py` | 仅加回调钩子 `_cb_push` + `flood_frequency`/初始水位读环境变量 + 反馈循环推送；**核心计算逻辑未改动** |

### 3.2 后端改造（backend-service）
| 文件 | 改动 |
|------|------|
| `app/services/water_sediment.py` | 新增 `WaterSedimentExecutor`（`async def run()`：`asyncio.create_subprocess_exec` 跑 `run_model_service.py`，读 result_file/stdout，返回 `TaskResult`） |
| `app/core/executor.py` | `TaskConfig` 加 `flood_frequency: str = "2年"` |
| `app/config.py` | 加 `river_model_root`（→`river_model/`）、`model_python`、`default_flood_frequency` |
| `app/schemas/job.py` | `RunRequest` 加 `flood_frequency`，`algorithm` 允许 `water_sediment` |
| `app/schemas/result.py` | `ResultResponse` 加 `result: dict | None`（承载水沙结构化结果） |
| `app/api/jobs.py` | `run()` 透传 `flood_frequency`；`get_results()` 区分 list/dict（dict 放 `result` 字段） |
| `app/core/job_manager.py` | 新增 `register_executor(algorithm, executor)`，worker 按 `algorithm` 路由执行器 |
| `app/main.py` | lifespan 注册 `water_sediment` → `WaterSedimentExecutor` |
| `app/services/matlab.py` | **MATLAB 可选容错**：启动失败不抛出，后端照常启动（水沙不受影响；NSGA-II/PAEM 返回"Engine 未就绪"） |

### 3.3 前端改造（frontend-service）
| 文件 | 改动 |
|------|------|
| `src/utils/waterSedimentCharts.ts` | 新增（**数据→图表适配**：模型 JSON → 系统 ECharts option，复用 `chart.ts`） |
| `src/components/water-sediment/WaterSedimentPanel.vue` | 新增（4 图 + 汇总卡：断面洪水/迭代收敛/龙羊峡调度/冲淤） |
| `src/types/model.ts` | `ConfigPlan` 加 `payload?` |
| `src/stores/modelConfig.ts` | `step4State` 加 `floodFrequency`；新增**多方案列表** `configPlans`/`addConfigPlan`/`removeConfigPlan`/`isCurrentPlanInList`/`resetConfigPlans` |
| `src/mock/model-config/dispatchScenario.ts` | "年内关键期调度 → 调水调沙" sub-option 启用（`active`） |
| `src/mock/model-config/modelAlgorithm.ts` | `dispatchModels` 加 `water_sediment` 模型 |
| `src/mock/model-config/linkage.ts` | `scenarioModelMap['critical-period']=['water_sediment']`、`scenarioSubOptionModelMap['sediment-period']='water_sediment'`、`modelLabelMap['water_sediment']` |
| `src/views/model-config/model-algorithm/ModelAlgorithmView.vue` | 水沙模型时用"重现期"选择器替代算法/目标卡 + 隐藏约束面板 |
| `src/views/model-config/config-summary/ConfigSummaryView.vue` | 多方案列表；每方案带 `payload`；"新增"→入列→`resetAll()`→跳 Step1；按行"运行"用该方案载荷；方案名按模型自动生成（`水沙方案-2年`、`缺水发电调度方案-NSGA-II`，同名加序号） |
| `src/views/process-transparent/ProcessTransparentView.vue` | 按算法分支：检测到水沙 `process_data`（含 `liujiaxia_outflow`/`sections`）→ 显示 `WaterSedimentPanel`；新增 `getProcessData` 初始补拉 |
| `src/views/evaluation-decision/EvaluationDecisionView.vue` | 水沙任务：显示水沙结果面板 + 说明，**不调用 postEvaluate** |
| `src/components/evaluation-decision/EvalTabNav.vue` | 加 `decisionDisabled`（水沙时禁用"决策分析"） |
| `src/api/index.ts` | `RunRequestPayload` 加 `flood_frequency`；新增 `getProcessData(jobId)` |

### 3.4 环境依赖
- 后端 conda 环境 **`yellow-river-web`**（Python 3.11.15）需包含：`numpy pandas scipy scikit-learn matplotlib openpyxl`（scikit-learn 为水沙 `data_processing.py` 所需，已补装）。
- `app/config.py` 的 `model_python` 默认为空 → 用 `sys.executable`（后端运行环境 python），需装有上述依赖；也可显式指定。

---

## 4. 部署 / 运行步骤

### 4.1 启动后端
```powershell
conda activate yellow-river-web     # 或用 D:\Anaconda\envs\yellow-river-web\python.exe
cd backend-service
python run.py                        # 0.0.0.0:18080
```
验证：`curl http://127.0.0.1:18080/health` → `{"status":"ok","engine":"ready"...}`。
> 无 MATLAB 时 `engine:"not started"`，但后端正常运行、水沙模型可用。

### 4.2 启动前端
```powershell
cd frontend-service
npm install
npm run dev                          # localhost:3000
```

### 4.3 界面操作（水沙模型）
1. 模型配置 → **Step1 调度场景** → 选 **「年内关键期调度」→「调水调沙」**
2. Step2/3 下一步 → **Step4 模型算法**（已自动选"水沙耦合仿真模型"）→ **选重现期**（2/5/10/50/100 年）
3. Step5 下一步 → **Step6 配置汇总** → 方案名显示 `水沙方案-2年` → **运行**
4. 过程透明页自动切换为水沙图表（断面洪水 / 迭代收敛 / 龙羊峡调度 / 冲淤，WS 实时推送）
5. 评价决策页：水沙任务显示水沙结果面板 + "无 Pareto 方案集，不参与多算法评价"；"决策分析"标签页禁用

### 4.4 多模型多方案
配置汇总可同时存在多个不同模型的方案（存于 Pinia store，跨步骤保留）：点"新增"→ 入列当前方案 → 跳回 Step1 → 选另一个场景/模型 → 配置完再回汇总，即多一个方案；每个方案可单独"运行"。

---

## 5. 验证记录

### 5.1 模型各重现期
| 频率 | 迭代数 | 兰州断面（头部流量） | 全河段冲淤 (m³) |
|------|--------|----------------------|------------------|
| 2年 | 21 | 1167→1235→1832→1858→1895 | -261067 |
| 5年 | 18 | — | -338089 |
| 10年 | 21 | 1535→1795→1857→1860→1854 | -375276 |
| 50年 | 14 | 1766→1783→1858→1862→1857 | -420683 |
| 100年 | 11 | 1747→1767→1830→1854→1852 | -415826 |

> 各频率兰州断面均收敛至控制区间 [1850, 1900]，反馈迭代 11~21 次收敛。

### 5.2 端到端联调（E2E）
POST `/run{algorithm:"water_sediment", flood_frequency:"2年"}` → 状态 `queued → running → completed`
- WebSocket 实时收到：**progress 22 条**（迭代1→21，0.5%→100%）+ **process_data 22 条**（每次迭代刘家峡下泄/兰州断面流量，末次含 8 断面 sections）
- `GET /process` 返回完整 `process_data`（flood_frequency/liujiaxia_outflow/sections/iteration_history/reservoir/sediment）
- `GET /results` 正常返回（`result` 字段承载水沙字典）

### 5.3 前端校验
- `npx vue-tsc --noEmit` 通过、`npx vite build` 通过。

---

## 6. 注意事项
- **模型定位差异**：水沙是**确定性仿真**，无 `evaluating` 矩阵 → 不参与 NMF/PP/AHP-FUZZY 评价；评价决策页对水沙任务已做优雅降级。
- **MATLAB 可选**：后端已容错，无 MATLAB 也能启动；NSGA-II/PAEM 任务会返回"Engine 未就绪"。
- **端口**：后端固定 18080；若改端口，`config.callback_url` 随之变化；MATLAB 侧 `http_callback_push.m` 写死 `127.0.0.1:18080/cb` 需同步。
- **运行时**：水沙模型单次约 **160 秒**（反馈迭代 + Excel 读写）；`POST /run` 异步返回 job_id，进度经 `/cb→WS` 实时刷新。
- **初始化**：若前端在任务结束后才连接，`getProcessData` 会补拉最新过程数据。
- **方案列表持久化**：目前存于内存（Pinia），刷新页面会清空；如需刷新不丢需后端方案表或 localStorage。
- **性能**：`coupledModel` 的 `get_power_output` 热循环反复读 Excel，后续可加缓存；模型有全局状态，多次调用建议子进程隔离（当前实现即子进程）。

---

## 7. 关键源码入口速查
| 环节 | 文件:行 |
|------|---------|
| 水沙执行器 | `backend-service/app/services/water_sediment.py` |
| 按算法路由 | `backend-service/app/core/job_manager.py` `register_executor` |
| 模型服务入口 | `river_model/run_model_service.py` |
| 拆分模块 | `river_model/mod_routing.py`、`river_model/mod_sediment.py` |
| 数据→图表 | `frontend-service/src/utils/waterSedimentCharts.ts` |
| 渲染组件 | `frontend-service/src/components/water-sediment/WaterSedimentPanel.vue` |
| 过程透明分支 | `frontend-service/src/views/process-transparent/ProcessTransparentView.vue` |
| 配置汇总多方案 | `frontend-service/src/views/model-config/config-summary/ConfigSummaryView.vue` |

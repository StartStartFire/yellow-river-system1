# 页面速查表（Pages Quick Reference）

> **定位**：页面原型已开发完成，本文档为修修改改样式时的速查手册。
> 代码即真相，本文档只写代码中不容易一眼看出来的东西（路由映射、状态颜色、跨步骤联动规则）。

---

## 1. 路由映射表

| 导航 | 路由 | View 文件 | 路由配置 |
|------|------|----------|---------|
| 首页 | `/home` | `src/views/home/HomeView.vue` | 默认路由 redirect |
| 基础数据 | `/basic-data` | `src/views/basic-data/BasicDataView.vue` | — |
| 水调水情 | `/water-condition` | `src/views/water-condition/WaterConditionView.vue` | — |
| 模型配置 | `/model-config` | redirect → `/model-config/dispatch-scenario` | — |
| 模型配置 Step 1 | `/model-config/dispatch-scenario` | `src/views/model-config/dispatch-scenario/DispatchScenarioView.vue` | — |
| 模型配置 Step 2 | `/model-config/dispatch-subject` | `src/views/model-config/dispatch-subject/DispatchSubjectView.vue` | — |
| 模型配置 Step 3 | `/model-config/model-data` | `src/views/model-config/model-data/ModelDataView.vue` | — |
| 模型配置 Step 4 | `/model-config/model-algorithm` | `src/views/model-config/model-algorithm/ModelAlgorithmView.vue` | — |
| 模型配置 Step 5 | `/model-config/scenario-constraint` | `src/views/model-config/scenario-constraint/ScenarioConstraintView.vue` | — |
| 模型配置 Step 6 | `/model-config/config-summary` | `src/views/model-config/config-summary/ConfigSummaryView.vue` | — |
| 过程透明 | `/process-transparent` | `src/views/process-transparent/ProcessTransparentView.vue` | — |
| 评价决策 | `/evaluation-decision` | `src/views/evaluation-decision/EvaluationDecisionView.vue` | — |
| 案例库 | `/case-library` | `src/views/case-library/CaseLibraryView.vue` | — |
| 报表统计 | `/report-statistics` | `src/views/report-statistics/ReportStatisticsView.vue` | — |

---

## 2. 首页（/home）

### 2.1 文件索引

| | 路径 |
|---|---|
| View | `src/views/home/HomeView.vue` |
| 子组件目录 | `src/components/home/` |
| Mock 数据 | `src/mock/home.ts` |
| 水库类型 | `src/types/reservoir.ts`（ReservoirBrief） |

### 2.2 子组件清单

| 组件 | 用途 |
|------|------|
| `ReservoirMap.vue` | Leaflet 地图：水库点位标注 + popup |
| `ReservoirMonitorPanel.vue` | 右侧浮层：水库水情监控（水位/流量/库容） |
| `PowerStatisticsPanel.vue` | 底部面板：出力统计图表 |
| `DispatchStatusBar.vue` | 顶部状态条：调度指令执行状态 |

### 2.3 公共组件使用

| 组件 | 使用位置 |
|------|---------|
| `PanelCard` | 水情监控卡片、出力统计面板 |
| `StatusTag` | 调度指令状态（"● 正常执行"，绿 + pulse）、水情监控"正常/预警/异常" |
| `BaseChart` | 出力统计图表 |
| `utils/format.ts` | 水位 `formatLevel`、流量 `formatFlow`、库容 `formatStorage` |

### 2.4 状态颜色映射

| 状态值 | 颜色 | StatusTag 用法 |
|--------|------|---------------|
| 正常 | `#00FF88` | `status="normal"` |
| 预警 | `#FFAA00` | `status="warning"` |
| 异常 | `#FF4D4F` | `status="abnormal"` |
| 调度指令状态"正常执行" | `#00FF88` | `label="正常执行" color="#00FF88" :pulse="true"` |

### 2.5 交互说明

- 地图点击水库点位 → 右侧面板切换到对应水库数据
- 右侧水库列表点击 → 地图定位到对应水库
- 底部面板可收起/展开
- 出力统计使用 `formatPower`（千分位整数，单位 MW）

---

## 3. 基础数据（/basic-data）

### 3.1 文件索引

| | 路径 |
|---|---|
| View | `src/views/basic-data/BasicDataView.vue` |
| 子组件目录 | `src/components/basic-data/` |
| Mock 数据 | `src/mock/basicData.ts` |
| 类型 | `src/types/reservoir.ts` |

### 3.2 子组件清单

| 组件 | 用途 |
|------|------|
| `ReservoirSidebar.vue` | 左侧水库列表（13 座，按龙羊峡以上/龙羊峡—刘家峡/刘家峡以下三组） |
| `BaseInfoPanel.vue` | 基础信息 Tab（工程属性 / 调度规则） |
| `EngineeringInfo.vue` | 工情信息（机组运行状态表格 + 泄洪闸门状态表格） |
| `KeyCurvesPanel.vue` | 关键曲线图表（库容 / 出力 / 过流） |
| `ReservoirSectionGraph.vue` | 水库断面示意图 |
| `MetricCards.vue` | 顶部指标卡片 |

### 3.3 公共组件使用

| 组件 | 使用位置 |
|------|---------|
| `PanelCard` | 基础信息卡片、工情信息卡片（机组 + 闸门两个表格各一个面板） |
| `StatusTag` | **机组状态**（`statusMap`：running→绿/stop→灰/maintenance→橙）+ 水库列表项状态（预设模式） |
| `BaseChart` | 关键曲线图表 |
| `utils/format.ts` | 水位 `formatLevel`、流量 `formatFlow`、出力 `formatNumber` |

### 3.4 状态颜色映射

| 状态值 | 颜色 | 位置 |
|--------|------|------|
| 运行（running） | `#00FF88` | 机组状态 |
| 停机（stop） | `#8aa0b8` | 机组状态 |
| 检修（maintenance） | `#f0a020` | 机组状态 |
| 正常 | `#00FF88` | 水库列表项（StatusTag preset） |
| 预警 | `#FFAA00` | 水库列表项 |
| 异常 | `#FF4D4F` | 水库列表项 |

### 3.5 交互说明

- 左侧点击水库 → 右侧三个面板（基础信息 / 工情信息 / 关键曲线）同步切换
- 工程信息中机组和闸门分两个独立的 PanelCard
- 水库共 13 座，分三组展示

---

## 4. 水调水情（/water-condition）

### 4.1 文件索引

| | 路径 |
|---|---|
| View | `src/views/water-condition/WaterConditionView.vue` |
| Mock 数据 | `src/mock/waterCondition.ts` |

### 4.2 子组件清单

无子组件，全部逻辑在 View 中。

### 4.3 公共组件使用

| 组件 | 使用位置 |
|------|---------|
| `PanelCard` | 图表分区 |
| `StatusTag` | 顶部"状态：正常执行"（绿 + pulse） |
| `BaseChart` | 核心过程图（入流/水位/出力/出流四个 Tab） |
| `utils/chart.ts` | `TEXT_SECONDARY`、`baseTooltip`、`baseCategoryXAxis`、`baseValueYAxis`、`createGrid`、`SERIES_COLORS` |
| `utils/format.ts` | 水位/流量/出力 |

### 4.4 状态颜色映射

| 状态值 | 颜色 | StatusTag 用法 |
|--------|------|---------------|
| 正常执行 | `#00FF88` | `label="正常执行" color="#00FF88" :pulse="true"` |

### 4.5 交互说明

- 筛选区：时间范围选择器 + 水库下拉框
- 指标 Tab：入流 / 水位 / 出力 / 出流（位于筛选栏最右侧，`margin-left: auto`）
- 无查询/重置按钮

---

## 5. 模型配置模块（6 步流程）

### 5.1 流程总览

```
Step 1 调度场景 → Step 2 调度主体 → Step 3 模型数据
     → Step 4 模型算法 → Step 5 场景配置 → Step 6 配置汇总
                                           ↓ 一键运行
                                      /process-transparent
```

### 5.2 Step 1：调度场景

| | 路径 |
|---|---|
| View | `src/views/model-config/dispatch-scenario/DispatchScenarioView.vue` |
| Mock | `src/mock/model-config/dispatchScenario.ts` |

**三大场景大类**（3 张卡片，grid-cols-3，互斥选择）：

| 大类 | 子选项 | 联动调度目标 |
|------|--------|------------|
| 多年的中长期调度 | 多目标优化调度 | flood-control, power-generation, ecology |
| 年内关键期调度 | 防洪期 / 防凌期 / 供水期 / 调水调沙 | 见下方映射表 |
| 实时调度 | 凌峰水沙调度 / 断面输沙调度 / 区间冲淤调度 / 多能互补 | 见下方映射表 |

**子选项→调度目标映射**（定义在 store `syncObjectivesFromScenario`）：

```
multi-objective → flood-control, power-generation, ecology
flood           → flood-control
ice             → flood-control
supply          → power-generation
sediment-period → sediment
ice-sediment    → flood-control, sediment
cross-section   → sediment
reach           → sediment
multi-energy    → multi-energy
```

### 5.3 Step 2：调度主体

| | 路径 |
|---|---|
| View | `src/views/model-config/dispatch-subject/DispatchSubjectView.vue` |
| Mock | `src/mock/model-config/dispatchSubject.ts` |

**预设水库组合**：

| 组合ID | 名称 | 水库 |
|--------|------|------|
| long-liu | 龙刘组合 | 龙羊峡、刘家峡 |
| long-liu-hei | 龙刘黑组合 | 龙羊峡、刘家峡、黑山峡 |
| all | 全部水库 | 13 座 |

**Step 1 → Step 2 联动**（场景时长约束）：

| Step 1 大类 | 时间范围约束 | 允许步长 |
|------------|------------|---------|
| 多年的中长期调度 | 1 年 ~ 5 年 | 每旬 / 每月 |
| 年内关键期调度 | ≤ 1 年（年内） | 每旬 / 每月 |
| 实时调度 | ≤ 31 天 | 仅每日（锁定） |

### 5.4 Step 3：模型数据

| | 路径 |
|---|---|
| View | `src/views/model-config/model-data/ModelDataView.vue` |
| Mock | `src/mock/model-config/modelData.ts` |

左侧目录 + 右侧图表/表格布局。数据目录包括入库与水位、西线调水、水位上下限、兰州断面需水等。

### 5.5 Step 4：模型算法

| | 路径 |
|---|---|
| View | `src/views/model-config/model-algorithm/ModelAlgorithmView.vue` |
| Mock | `src/mock/model-config/modelAlgorithm.ts`、`linkage.ts` |

**左右分区**：左 65%（模型选择 + 算法选择 + 参数编辑）/ 右 35%（调度目标 + 约束条件弹窗入口）

**支持的模型**：lro（水库群优化调度）、multi_objective_stress（多目标协同胁迫）、multi_objective_dispatch（多目标优化调度）、water_sediment_realtime（水沙实时调度）

**支持的算法**：NSGA-II / PSO / PAEM / NSGA-III

**Step 2 → Step 4 联动**：`compatibleModels` 计算属性从 `reservoirGroupModelMap` 过滤模型列表。

**约束条件在 Step 4 弹窗中编辑**。

### 5.6 Step 5：场景配置

| | 路径 |
|---|---|
| View | `src/views/model-config/scenario-constraint/ScenarioConstraintView.vue` |
| Mock | `src/mock/model-config/scenarioConstraint.ts`、`linkage.ts` |

典型场景 / 自定义场景切换 + 场景参数（西线调水、调沙流量、冲沙流量、生态流量、防凌流量）。

**Step 4 → Step 5 联动**：`relevantScenarioParamIds` 计算属性根据 `step4State.selectedObjectives` 高亮关联参数。

### 5.7 Step 6：配置汇总

| | 路径 |
|---|---|
| View | `src/views/model-config/config-summary/ConfigSummaryView.vue` |
| Mock | `src/mock/model-config/configSummary.ts` |

左侧配置方案表格 + 右侧预计计算信息。底部独立布局（非 ModelConfigFooter）：上一步 / 一键运行 / 导出配置。

**详情弹窗**读取 `store.dispatchScenario` / `dispatchSubject` / `modelData` / `modelAlgorithm` / `scenarioConstraint`（即 step1State~step5State）。弹窗按 5 块分区展示。

**公共组件**：表格使用 `PanelCard accent` + `#header-actions` 插槽承载新增/筛选/搜索按钮。

### 5.8 Store 字段速查

| Store key（外部别名） | 内部变量 | 所属步骤 | 主要字段 |
|----------------------|---------|---------|---------|
| `dispatchScenario` | `step1State` | Step 1 | categoryId, subOptionId, scenarioName |
| `dispatchSubject` | `step2State` | Step 2 | startTime, endTime, timeStep, scheduleFrequency, selectedReservoirIds, selectedGroupId |
| `modelData` | `step3State` | Step 3 | activeMenuId, dateRange, selectedDataIds |
| `modelAlgorithm` | `step4State` | Step 4 | selectedModel, selectedAlgorithm, selectedObjectives, parameters |
| `scenarioConstraint` | `step5State` | Step 5 | scenarioType, scenarioDescription, params |

**步骤间联动计算属性**：`compatibleModels`（Step 2→4）、`relevantScenarioParamIds`（Step 4→5）

### 5.9 Mock 数据目录

```
src/mock/model-config/
├─ dispatchScenario.ts       # Step 1 数据
├─ dispatchSubject.ts        # Step 2 数据
├─ modelData.ts              # Step 3 数据
├─ modelAlgorithm.ts         # Step 4 数据
├─ scenarioConstraint.ts     # Step 5 数据
├─ configSummary.ts          # Step 6 数据
└─ linkage.ts                # 跨步骤联动映射
```

引用方式：直接 import 子模块。

### 5.10 公共组件使用

| 组件 | 使用位置 |
|------|---------|
| `PanelCard` | 各步骤内容分区 |
| `StatusTag` | 水库状态、方案状态等 |
| `BaseChart` | 模型数据概览图表（Step 3） / 模型算法分布图（Step 6） |

---

## 6. 过程透明（/process-transparent）

### 6.1 文件索引

| | 路径 |
|---|---|
| View | `src/views/process-transparent/ProcessTransparentView.vue` |
| Mock | `src/mock/processTransparent.ts` |

### 6.2 公共组件使用

| 组件 | 使用位置 |
|------|---------|
| `PanelCard` | 底部 5 个辅助卡片（运行日志/最优方案/约束满足/预估摘要/操作） |
| `StatusTag` | 任务状态（运行中→绿+pulse / 已完成→蓝 / 已终止→红） |
| `BaseChart` | 6 个图表（收敛曲线 + 目标趋势 + 2×Tab 水位/流量/出力） |
| `utils/chart.ts` | `TECH_CYAN_LIGHT`、`baseTooltip`、`baseCategoryXAxis` 等（注意：`TECH_CYAN_LIGHT` 已修复导入） |
| `utils/format.ts` | 水位/流量/出力 |

### 6.3 状态颜色映射

| 状态值 | 颜色 | StatusTag 用法 |
|--------|------|---------------|
| 运行中 | `#00ff88` | `:label="status" :color="statusColor" :pulse="true"` |
| 已完成 | `var(--tech-blue)` | `:label="status" :color="statusColor"` |
| 已终止 | `#ff4d4f` | `:label="status" :color="statusColor"` |

**注意**：状态值必须用中文，禁止 `'running'` 等英文。`statusColor` 通过 computed 映射。

### 6.4 交互说明

- 顶部方案情景选择区（多张卡片）
- 状态栏：任务状态 + 调度周期 + 已运行/预计剩余时间 + 进度条
- 中部：左 40% 优化过程（收敛曲线 + 目标趋势）+ 右 60% 水库运行响应（龙羊峡/刘家峡 × 水位/流量/出力 Tab）
- 底部 5 个卡片：运行日志 + 当前最优方案信息 + 约束满足情况 + 预估结果摘要 + 操作
- 底部卡片使用 PanelCard，紧凑样式通过 `:deep(.section-header)` 等微调
- 进度模拟使用 setInterval，100% 后自动变为"已完成"
- 日志追加模拟使用 setInterval

---

## 7. 评价决策（/evaluation-decision）

### 7.1 文件索引

| | 路径 |
|---|---|
| View | `src/views/evaluation-decision/EvaluationDecisionView.vue` |
| 子组件目录 | `src/components/evaluation-decision/` |
| Mock | `src/mock/evaluationDecision.ts` |

### 7.2 子组件清单

| 组件 | 用途 |
|------|------|
| `EvaluationPanel.vue` | 评价分析 Tab：雷达图 + 帕累托散点图 + 排名条形图 + 评价表 |
| `DecisionPanel.vue` | 决策分析 Tab：桑基图 + 过程曲线 + 目标满足列表 |
| `ScenarioSelector.vue` | 方案情景选择器 |

### 7.3 公共组件使用

| 组件 | 使用位置 |
|------|---------|
| `PanelCard` | 评价/决策各分区 |
| `StatusTag` | 目标满足状态（已满足→绿 / 基本满足→橙 / 未满足→红） |
| `BaseChart` | 雷达图 / 桑基图 / 帕累托 / 过程曲线 / 排名条形图 |
| `utils/chart.ts` | 图表配置工厂 |
| `utils/format.ts` | `formatScore`（评价得分 3 位小数）、`formatPercent`（完成率百分比） |

### 7.4 状态颜色映射

| 状态值 | 颜色 | StatusTag 用法 |
|--------|------|---------------|
| 已满足 | `#00FF88` | `status="normal"` |
| 基本满足 | `#FFAA00` | `status="warning"` |
| 未满足 | `#FF4D4F` | `status="abnormal"` |

### 7.5 交互说明

- Tab 导航切换：评价分析 / 决策分析
- 评价分析：雷达图可切换三种评价维度（综合/防洪/发电），帕累托散点 + 排名条
- 决策分析：桑基图 + 3 张过程曲线 + 目标满足列表（space-evenly 分布）
- 评价表格使用 `.dark-table`

---

## 8. 案例库（/case-library）

### 8.1 文件索引

| | 路径 |
|---|---|
| View | `src/views/case-library/CaseLibraryView.vue` |
| 子组件目录 | `src/components/case-library/` |
| Mock | `src/mock/caseLibrary.ts` |

### 8.2 子组件清单

| 组件 | 用途 |
|------|------|
| `CaseFilter.vue` | 筛选条件（年份/季节/场景/模型/算法/关键词） |
| `CaseList.vue` | 案例列表表格（排序/搜索/分页） |
| `CaseDetailPanel.vue` | 案例详情（右侧面板） |
| `CaseComparePanel.vue` | 案例对比面板 |

### 8.3 公共组件使用

| 组件 | 使用位置 |
|------|---------|
| `PanelCard` | 案例列表区 / 详情区 / 关键指标卡片 |
| `StatusTag` | 案例状态（已验证→绿 / 已归档→蓝 / 待复核→橙 / 草稿→灰） |
| `BaseChart` | 过程曲线预览 |
| `utils/format.ts` | `formatScore`（综合评分）、`formatPercent`（占比） |

### 8.4 状态颜色映射

| 状态值 | 颜色 | StatusTag 用法 |
|--------|------|---------------|
| 已验证 | `#00FF88` | `label="已验证" color="#00FF88"` |
| 已归档 | `var(--tech-blue)` | `label="已归档" color="var(--tech-blue)"` |
| 待复核 | `#FFAA00` | `label="待复核" color="#FFAA00"` |
| 草稿 | `#8aa0b8` | `label="草稿" color="#8aa0b8"` |

### 8.5 交互说明

- 顶部筛选区（年份/季节/场景/模型/算法/关键词）
- 左侧案例列表表格 + 右侧案例详情面板（或弹窗显示）
- 支持案例对比（多选后并排展示）
- 案例列表使用 `.dark-table`

---

## 9. 报表统计（/report-statistics）

### 9.1 文件索引

| | 路径 |
|---|---|
| View | `src/views/report-statistics/ReportStatisticsView.vue` |
| Mock | `src/mock/reportStatistics.ts` |

### 9.2 子组件清单

无子组件，全部逻辑在 View 中。

### 9.3 公共组件使用

| 组件 | 使用位置 |
|------|---------|
| `PanelCard` | 各表块 |
| `StatusTag` | 考核结果（达标→绿 / 接近阈值→橙 / 未达标→红） |
| `utils/format.ts` | `formatNumber`（一般数值）、`formatThousands`（千分位）、`formatPercent`（百分比） |

### 9.4 状态颜色映射

| 状态值 | 颜色 | StatusTag 用法 |
|--------|------|---------------|
| 达标 | `#00FF88` | `status="normal"` |
| 接近阈值 | `#FFAA00` | `status="warning"` |
| 未达标 | `#FF4D4F` | `status="abnormal"` |

### 9.5 交互说明

- 表格展示，使用 `.dark-table` 全局类
- 当前阶段不做真实导出

---

## 10. 全站状态颜色速查

| 业务状态 | 颜色 | StatusTag 用法 | 出现页面 |
|---------|------|---------------|---------|
| 正常 / 在线 / 运行中 | `#00FF88` | `status="normal"` 或 `label` + `color="#00FF88"` | 首页 / 基础数据 / 水调水情 / 过程透明 |
| 预警 / 关注 / 风险 / 基本满足 / 接近阈值 | `#FFAA00` | `status="warning"` | 首页 / 基础数据 / 评价决策 / 报表统计 |
| 异常 / 告警 / 超限 / 未满足 / 未达标 | `#FF4D4F` | `status="abnormal"` | 首页 / 基础数据 / 评价决策 / 报表统计 |
| 已完成 / 已归档 | `var(--tech-blue)` | `label="已完成" color="var(--tech-blue)"` | 过程透明 / 案例库 |
| 已终止 | `#ff4d4f` | `label="已终止" color="#ff4d4f"` | 过程透明 |
| 检修 | `#f0a020` | `label="检修" color="#f0a020"` | 基础数据（机组状态） |
| 停机 | `#8aa0b8` | `label="停机" color="#8aa0b8"` | 基础数据（机组状态） |
| 草稿 | `#8aa0b8` | `label="草稿" color="#8aa0b8"` | 案例库 |
| 待复核 | `#FFAA00` | `label="待复核" color="#FFAA00"` | 案例库 |
| 已验证 | `#00FF88` | `label="已验证" color="#00FF88"` | 案例库 |
| 运行中（pulse 动画） | `#00ff88` | `label="运行中" color="#00ff88" :pulse="true"` | 过程透明 |

### 10.1 颜色值速查

| 色值 | CSS 变量/硬编码 | 用途 |
|------|----------------|------|
| `#00FF88` | 硬编码 | 正常/运行/达标/已验证 |
| `#FFAA00` | 硬编码 | 预警/关注/基本满足/待复核 |
| `#FF4D4F` | 硬编码 | 异常/未满足/已终止 |
| `var(--tech-blue)` | CSS 变量 | 已完成/已归档 |
| `#f0a020` | 硬编码 | 检修（特殊业务色） |
| `#8aa0b8` | 硬编码 | 停机/草稿 |

---

## 11. 常用格式化函数速查

| 函数 | 文件 | 用途 | 示例 |
|------|------|------|------|
| `formatLevel(value)` | `utils/format.ts` | 水位（2 位小数 + m） | `formatLevel(2472.35)` → `"2472.35 m"` |
| `formatFlow(value)` | `utils/format.ts` | 流量（1 位小数 + m³/s） | `formatFlow(1250)` → `"1250.0 m³/s"` |
| `formatStorage(value)` | `utils/format.ts` | 库容（2 位小数 + 亿 m³） | `formatStorage(247.58)` → `"247.58 亿 m³"` |
| `formatPower(value)` | `utils/format.ts` | 发电量（千分位整数 + MW） | `formatPower(1280000)` → `"1,280,000 MW"` |
| `formatScore(value)` | `utils/format.ts` | 评价得分（3 位小数） | `formatScore(0.856)` → `"0.856"` |
| `formatPercent(value)` | `utils/format.ts` | 百分比 | `formatPercent(0.856)` → `"85.6%"` |
| `formatNumber(value, digits)` | `utils/format.ts` | 通用数字 | `formatNumber(1234.567, 1)` → `"1234.6"` |
| `formatThousands(value)` | `utils/format.ts` | 千分位 | `formatThousands(1234567)` → `"1,234,567"` |

---

## 12. 跨页面业务流程图

```
首页（地图 + 水库监控）
  │
  ├─ 基础数据（选水库 → 查属性/工情/曲线）
  │
  ├─ 模型配置（6 步流程）
  │     Step 1 调度场景 → Step 2 调度主体 → Step 3 模型数据
  │          → Step 4 模型算法 → Step 5 场景配置 → Step 6 配置汇总
  │                                                       ↓ 一键运行
  │                                                  过程透明
  │                                                 （模拟计算过程）
  │                                                       ↓ 计算完成
  │                                                  评价决策
  │                                                 （Tab：评价/决策）
  │
  ├─ 案例库（历史方案浏览 + 对比 + 复现）
  │
  ├─ 报表统计（报表表格展示）
  │
  └─ 水调水情（实时水情图表）
```
